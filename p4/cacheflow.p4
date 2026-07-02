/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x0800;

// 定义报文头部结构
typedef bit<9>  egress_port_t;
typedef bit<32> ipv4_addr_t;

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    tcp_t        tcp;
    udp_t        udp;
}

// 五元组匹配键
struct tuple_5tuple_t {
    ipv4_addr_t src_addr;
    ipv4_addr_t dst_addr;
    bit<8>      protocol;
    bit<16>     src_port;
    bit<16>     dst_port;
}

// 解析器
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            6: parse_tcp;
            17: parse_udp;
            default: accept;
        }
    }
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }
}

// 逆解析器
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
        packet.emit(hdr.udp);
    }
}

// ============================================================
// CacheFlow 核心：TCAM模拟表 + 统计寄存器
// ============================================================
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    // -------- 动作定义 --------
    action forward(egress_port_t port) {
        standard_metadata.egress_spec = port;
    }

    action drop_action() {
        mark_to_drop(standard_metadata);
    }

    action send_to_cpu() {
        standard_metadata.egress_spec = 0x80;  // CPU端口
    }

    action no_action() { }

    // -------- 缓存表（模拟TCAM，支持优先级） --------
    table cache_table {
        key = {
            hdr.ipv4.srcAddr   : ternary;
            hdr.ipv4.dstAddr   : ternary;
            hdr.ipv4.protocol  : ternary;
            hdr.tcp.srcPort    : ternary;
            hdr.tcp.dstPort    : ternary;
        }
        actions = {
            forward;
            drop_action;
            send_to_cpu;
            no_action;
        }
        size = 1024;
        default_action = send_to_cpu;
    }

    // -------- 命中/未命中统计寄存器 --------
    register<bit<32>>(1) hit_cnt;
    register<bit<32>>(1) miss_cnt;

    // -------- 数据面入口逻辑 --------
    apply {
        // 查表
        cache_table.apply();

        // 根据动作类型更新统计（简化：查表后根据结果计数）
        // 实际生产环境可由控制平面读取寄存器
        if (standard_metadata.egress_spec == 0x80) {
            miss_cnt.add(1, 1);
        } else {
            hit_cnt.add(1, 1);
        }
    }
}

// 入口流水线
control MyIngressPipeline(inout headers hdr,
                          inout metadata meta,
                          inout standard_metadata_t standard_metadata) {
    apply {
        MyIngress.apply(hdr, meta, standard_metadata);
    }
}

// 主模块
V1Switch(
    MyParser(),
    MyIngressPipeline(),
    MyIngressPipeline(),  // egress（复用）
    MyDeparser()
) main;
