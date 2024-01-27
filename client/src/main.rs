use api::{
    my_service_client::MyServiceClient, AddFirewallRuleRequest, ChangeWeightRequest, Link, Node,
    RateRequest, SetEncapRequest, SwapRequest,
};
use std::env;
use std::fs;
use tonic::{transport::Channel, Request};
use view_graph::evacuate;
pub mod api {
    tonic::include_proto!("myservice");
}
use std::process::Command;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        println!("Usage:./client <action> <node> [additional_args]");
        return Ok(());
    }

    let action = (&args[1]).as_str();
    let node = Node {
        node: (&args[2]).clone(),
    };

    let channel = Channel::from_static("http://localhost:50051")
        .connect()
        .await?;

    let mut client = MyServiceClient::new(channel);

    match action {
        // "list" => {
        //     let rep = client.list_node(Request::new(api::Empty {})).await?;
        //     println!("list response: {:?}", rep.into_inner().nodes);
        // }
        "stat" => {
            let rep = client.get_stat(Request::new(node)).await?;
            println!("Stat response: {:?}", rep.into_inner().stat_info);
        }
        "reset" => {
            let rep = client.reset(Request::new(node)).await?;
            println!("Reset response: {:?}", rep.into_inner().message);
        }

        "fw" => {
            // if number of arg not match return helper for fw
            let reqest = AddFirewallRuleRequest {
                node: node.node,
                source_ip: args[3].clone(),
                dest_ip: args[4].clone(),
                protocol: args[5].clone(),
                source_port: args[6].parse().unwrap(),
                dest_port: args[7].parse().unwrap(),
            };
            let rep = client.add_firewall_rule(Request::new(reqest)).await?;
            println!("fw response: {:?}", rep.into_inner().message);
        }
        "rate" => {
            let rep = client
                .change_rate(Request::new(RateRequest {
                    node: node.node,
                    rate: args[3].parse().unwrap(),
                }))
                .await?;
            println!("rate response: {:?}", rep.into_inner().result);
        }

        "encap" => {
            let rep = client
                .set_encap(Request::new(SetEncapRequest {
                    node: node.node,
                    ip_address: args[3].parse().unwrap(),
                    nodedst: args[4].clone(),
                }))
                .await?;
            println!("encap response: {:?}", rep.into_inner().answer);
        }

        "weight" => {
            let rep = client
                .change_weight(Request::new(ChangeWeightRequest {
                    lien: Some(Link {
                        node_a: args[2].clone(),
                        node_b: args[3].clone(),
                    }),
                    weight: args[4].parse().unwrap(),
                }))
                .await?;
            println!("weight response: {:?}", rep.into_inner().status);
        }

        "add" => {
            let rep = client
                .add_link(Request::new(Link {
                    node_a: node.node,
                    node_b: args[3].clone(),
                }))
                .await?;
            println!("add response: {:?}", rep.into_inner().status);
        }

        "remove" => {
            let rep = client
                .remove_link(Request::new(Link {
                    node_a: node.node,
                    node_b: args[3].clone(),
                }))
                .await?;
            println!("remove response: {:?}", rep.into_inner().status);
        }

        "swap" => {
            let rep = client
                .swap_controler(Request::new(SwapRequest {
                    target: Some(node),
                    mode: args[3].clone(),
                    argument: args[4..].to_vec(),
                }))
                .await?;
            println!("swap response: {:?}", rep.into_inner().status);
        }

        "show" => {
            let rep = client
                .show_topo(Request::new(api::Empty {  }))
                .await?;
            let thejson:String = rep.into_inner().mon_json;
            evacuate(thejson.clone());
            Command::new("geeqie").args(["/tmp/topology.png"]).output().unwrap();
        }
        // Ajoutez les autres cas d'action ici, en suivant le même schéma.
        _ => {
            println!("Unknown action: {}", action);
        }
    }

    Ok(())
}
