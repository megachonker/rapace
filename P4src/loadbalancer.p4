/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

//My includes
#include "include/headers.p4"
#include "include/parsers.p4"



/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {


    
    
    direct_meter<bit<32>>(MeterType.packets) the_meter;// to control traffic on each port
    counter(1, CounterType.packets_and_bytes) total_packet;

    
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ecmp_group( bit<16> num_nhops){
        hash(meta.ecmp_hash,
	    HashAlgorithm.crc16,
	    (bit<1>)0,
	    { hdr.ipv4.srcAddr,
	      hdr.ipv4.dstAddr,
          hdr.tcp.srcPort + hdr.udp.srcPort,
          hdr.tcp.dstPort + hdr.udp.dstPort,
          hdr.ipv4.protocol},
	    num_nhops);

    }



    //We need to declare to set_nhop action beacause for in_out, the traffic must be control (1 p/S for e.g ) We consider that fotr the out_in it is not control
    action set_nhop_in_out(macAddr_t dstAddr, egressSpec_t port) {

        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;

        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;

        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;

        the_meter.read(meta.meter_tag);
    }


    action set_nhop_out_in(macAddr_t dstAddr, egressSpec_t port) {


        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;

        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;

        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }


    table ecmp_group_to_nhop {
        key = {
            meta.ecmp_hash: exact;
        }
        actions = {
            drop;
            set_nhop_in_out;
        }
        size = 1024;
        meters = the_meter; //meter on each port 
    }

    table traffic_type {
        //This table check where the packet from (if it is from in port -> load balance, out ports -> just forward to in port)
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            set_nhop_out_in;
            ecmp_group;
            drop;
        }
        size = 1024;
        default_action = drop;
    }

    table filter {

        key = {
            meta.meter_tag : exact;
        }


        actions = {
            NoAction;
            drop;
        }
        size = 1024;
    }

    apply {
        total_packet.count((bit<32>)0);
        if (hdr.ipv4.isValid()){
            switch (traffic_type.apply().action_run){
                ecmp_group: {
                    ecmp_group_to_nhop.apply();
                    filter.apply();
                }
            }
        }

        //ttl check
        if (hdr.ipv4.ttl == 0){
            mark_to_drop(standard_metadata);
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {

    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	          hdr.ipv4.ihl,
              hdr.ipv4.dscp,
              hdr.ipv4.ecn,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
              hdr.ipv4.hdrChecksum,
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