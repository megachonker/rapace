/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

//My includes
#include "include/headers.p4"

/*************************************************************************
*********************** P A R S E R  *******************************
*************************************************************************/


parser MyParser(packet_in packet,
                out headers_stacked hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4.next);
        transition accept;
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers_stacked hdr) {
    apply {

        //parsed headers_stacked have to be added again into the packet.
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers_stacked hdr, inout metadata meta) {
    apply {}
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers_stacked hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    counter(1, CounterType.packets_and_bytes) total_packet;

    action pass(){
        //do nothing
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action decap(){
        hdr.ipv4.pop_front(1);
    }

    // source are actually loopback
    action encap(ip4Addr_t source,ip4Addr_t destination){
        //fait de la place pour un nouveaux header
        hdr.ipv4.push_front(1);
        hdr.ipv4[0].srcAddr=source;
        hdr.ipv4[0].dstAddr=destination;
    }


    action forward(macAddr_t dstAddr, egressSpec_t port) {
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;

        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;

        hdr.ipv4[0].ttl = hdr.ipv4[0].ttl - 1;
    }

    table encap_table{
        key = {
            hdr.ipv4[0].dstAddr : exact;
        }
        actions = {
            decap;
            encap;
            pass;
        }
        size = 1024;
        default_action = pass;
    }


    table ipv4_lpm {
        key = {
            hdr.ipv4[0].dstAddr : exact;
        }
        actions = {
            forward;
            drop;
        }
        size = 1024;
        default_action = drop;
    }


    apply {
        total_packet.count((bit<32>)0);
        encap_table.apply();
        ipv4_lpm.apply();
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers_stacked hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {}
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers_stacked hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4[0].isValid(),
            { hdr.ipv4[0].version,
	          hdr.ipv4[0].ihl,
              hdr.ipv4[0].dscp,
              hdr.ipv4[0].ecn,
              hdr.ipv4[0].totalLen,
              hdr.ipv4[0].identification,
              hdr.ipv4[0].flags,
              hdr.ipv4[0].fragOffset,
              hdr.ipv4[0].ttl,
              hdr.ipv4[0].protocol,
              hdr.ipv4[0].srcAddr,
              hdr.ipv4[0].dstAddr },
              hdr.ipv4[0].hdrChecksum,
              HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;