/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

const bit<16> TYPE_IPV4 = 0x800;

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;


header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<6>    dscp;
    bit<2>    ecn;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

// header tcp_t{
//     bit<16> srcPort;
//     bit<16> dstPort;
//     bit<32> seqNo;
//     bit<32> ackNo;
//     bit<4>  dataOffset;
//     bit<4>  res;
//     bit<1>  cwr;
//     bit<1>  ece;
//     bit<1>  urg;
//     bit<1>  ack;
//     bit<1>  psh;
//     bit<1>  rst;
//     bit<1>  syn;
//     bit<1>  fin;
//     bit<16> window;
//     bit<16> checksum;
//     bit<16> urgentPtr;
// }

struct metadata {
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    // tcp_t        tcp;
}

/*************************************************************************
*********************** P A R S E R  *******************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
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
        packet.extract(hdr.ipv4);
        transition accept;

        // transition select(hdr.ipv4.protocol){
        //     6 : parse_tcp;
        //     default: accept;
        // }
    }

    // state parse_tcp {
    //     packet.extract(hdr.tcp);
    //     transition accept;
    // }
}

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

    action forward(bit<9> egress_port){
        standard_metadata.egress_spec = egress_port;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action allow(){
        //do nothing it is corect way ?
    }

    table rule {
        key = {
            hdr.ipv4.srcAddr: exact;
            hdr.ipv4.dstAddr: exact;
            // hdr.ipv4.protocol: exact;
            // hdr.tcp.srcPort: exact;
            // hdr.tcp.dstPort: exact;
        }
        actions = {
            allow;
            drop;
        }
        size = 2;
        default_action = allow;
    }


    table route {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            forward;
            drop;
        }
        size = 2;
        default_action = drop;
    }

    apply {
        //check if allowed
        if  (! rule.apply().hit){
            route.apply();
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

control MyDeparser(packet_out packet, in headers hdr) {
    apply {

        // //parsed headers have to be added again into the packet.
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);

        // //Only emited if valid
        // packet.emit(hdr.tcp);
    }
}
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