/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parsers.p4"
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/



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

    // counter
    direct_counter(CounterType.packets) filter_hit;
    counter(1, CounterType.packets_and_bytes) total_packet;

    action forward(macAddr_t dstAddr, egressSpec_t port) {
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;

        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action allow(){
        //NoAction
    }  

    table rule {  //table to check if the packet match a rule (if drop it)
        key = {
            hdr.ipv4.srcAddr: exact;
            hdr.ipv4.dstAddr: exact;
            hdr.ipv4.protocol: exact;
            hdr.tcp.srcPort + hdr.udp.srcPort: exact @name("src port number");    //add both because one of the two is zero
            hdr.tcp.dstPort + hdr.udp.dstPort: exact @name("dest port number");
        }
        actions = {
            allow;
            drop;
        }
        size = 2;
        default_action = allow;     //if any rule match allow the packet 
        counters=filter_hit;
    }


    table route {               //foraward the packet to the corresponding port
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            forward;
            drop;
        }
        size = 2;
        default_action = drop;
        // counters=filter_hit;
    }

    apply {
        total_packet.count((bit<32>)0);
        //check if allowed
        if  (! rule.apply().hit){
            route.apply();
        }
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
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply { }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;