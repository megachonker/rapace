use api::{
    my_service_client::MyServiceClient, AddFirewallRuleRequest, ChangeWeightRequest, Link, Node,
    RateRequest, SetEncapRequest, SwapRequest,SetEncapLinkRequest
};
use tonic::{transport::Channel, Request};
use view_graph::evacuate;
pub mod api {
    tonic::include_proto!("myservice");
}
use std::process::Command;

use rustyline::error::ReadlineError;
use rustyline::DefaultEditor;

fn read_command(rl: &mut rustyline::Editor<(), rustyline::history::FileHistory>) -> Option<String> {
    // `()` can be used when no completer is required
    loop {
        let readline = rl.readline("RAPACE_CLI> ");
        match readline {
            Ok(line) => {
                rl.add_history_entry(line.as_str()).unwrap();
                return Some(line);
            }
            Err(ReadlineError::Interrupted) => {
                continue;
            }
            Err(ReadlineError::Eof) => {
                println!("Exit");
                break;
            }
            Err(err) => {
                println!("Error: {:?}", err);
                break;
            }
        }
    }
    None
}

fn print_help() {
    println!("Available actions:");
    println!("  stat <node>                                            - Get statistics of node");
    println!("  reset <node>                                           - Reset the node");
    println!("  fw <node> <args>                                       - Add firewall rule");
    println!("  rate <node> <pkt/s>                                    - Change rate of the loadbalancer ");
    println!("  encap <node> <args>                                    - Set encapsulation");
    println!("  weight <node1> <node2> <new_weight>                    - Change weight of link node1-node2");
    println!("  add <node1> <node2>                                    - Add link node1-node2");
    println!("  remove <node1> <node2>                                 - Remove link node1-node2 (if it possible)");
    println!("  swap <node> <role> [neigboor1 neigboor2 ...]           - Swap role of the node and spécify the neighboor");
    println!("  show topology                                          - Show topology");

    // Ajoutez les informations d'utilisation pour d'autres actions ici.
}

async fn action_match(
    action: &str,
    client: &mut MyServiceClient<Channel>,
    args: &mut Vec<String>,
) -> Result<(), Box<dyn std::error::Error>> {
    let node = if args.len() > 1 {
        Node {
            node: String::from(args.get(1).unwrap_or(&"".to_string()).clone()),
        }
    } else {
        Node {
            node: String::from(""),
        }
    };

    // for _ in 0..4 {
    //     args.push("".into());
    // }
    

    match action {
        "stat" => {
            let rep = client.get_stat(Request::new(node)).await?;
            let rep : String = rep.into_inner().stat_info;
            println!("{rep}");
        }
        "reset" => {
            let rep = client.reset(Request::new(node)).await?;
            println!("{:?}", rep.into_inner().message);
        }

        "fw" => {
            // if number of arg not match return helper for fw
            let reqest = AddFirewallRuleRequest {
                node: node.node,
                source_ip: args.get(2).unwrap_or(&"".to_string()).clone(),
                dest_ip: args.get(3).unwrap_or(&"".to_string()).clone(),
                protocol: args.get(5).unwrap_or(&"".to_string()).clone(),
                source_port: args.get(6).unwrap_or(&"".to_string()).parse().unwrap(),
                dest_port: args.get(7).unwrap_or(&"".to_string()).parse().unwrap(),
            };
            let rep = client.add_firewall_rule(Request::new(reqest)).await?;
            println!("{:?}", rep.into_inner().message);
        }
        "rate" => {
            let rep = client
                .change_rate(Request::new(RateRequest {
                    node: node.node,
                    rate: args.get(2).unwrap_or(&"".to_string()).parse().unwrap(),
                }))
                .await?;
            println!("{:?}", rep.into_inner().result);
        }

        "encap" => {
            let rep;
            if args.len() == 6{
                rep =client.set_encap_link(Request::new(SetEncapLinkRequest {
                    node: node.node,
                    ip_address: args[3].parse().unwrap(),
                    nodedst_a: args[4].clone(),
                    nodedst_b: args[5].clone(),
                }))
                .await?;
            }else{
                rep = client
                .set_encap(Request::new(SetEncapRequest {
                    node: node.node,
                    ip_address: args.get(2).unwrap_or(&"".to_string()).parse().unwrap(),
                    nodedst: args.get(3).unwrap_or(&"".to_string()).clone(),
                }))
                .await?;
            }

            println!("{:?}", rep.into_inner().answer);
        }

        "weight" => {
            let rep = client
                .change_weight(Request::new(ChangeWeightRequest {
                    lien: Some(Link {
                        node_a: args.get(1).unwrap_or(&"".to_string()).clone(),
                        node_b: args.get(2).unwrap_or(&"".to_string()).clone(),
                    }),
                    weight: args.get(3).unwrap_or(&"".to_string()).parse().unwrap_or(1),
                }))
                .await?;
            println!("{:?}", rep.into_inner().status);
        }

        "add" => {
            let rep = client
                .add_link(Request::new(Link {
                    node_a: node.node,
                    node_b: args.get(2).unwrap_or(&"".to_string()).clone(),
                }))
                .await?;
            println!("{:?}", rep.into_inner().status);
        }

        "remove" => {
            let rep = client
                .remove_link(Request::new(Link {
                    node_a: node.node,
                    node_b: args.get(2).unwrap_or(&"".to_string()).clone(),
                }))
                .await?;
            println!("{:?}", rep.into_inner().status);
        }

        "swap" => {
            let mut arg = vec![];
            if args.len()>3{
                arg = args[3..].to_vec();
            }
            let rep = client
                .swap_controler(Request::new(SwapRequest {
                    target: Some(node),
                    mode: args.get(2).unwrap_or(&"".to_string()).clone(),
                    argument: arg,
                }))
                .await?.into_inner().status;
            println!("Sucess of swap {rep}");
        }

        "show" => {
            let rep = client.show_topo(Request::new(api::Empty {})).await?;
            let thejson: String = rep.into_inner().mon_json;
            evacuate(thejson.clone());
            Command::new("geeqie")
                .args(["/tmp/topology.png"])
                .output()
                .unwrap();
        }

        "help" => print_help(),
        _ => {
            println!("Unknown action: {}", action);
        }
    }
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // let args: Vec<String> = env::args().collect();

    // if args.len() < 3 {
    //     println!("Usage:./client <action> <node> [additional_args]");
    //     return Ok(());
    // }

    // let action = (&args.get(1).unwrap_or(&"".to_string())).as_str();
    // let node = Node {
    //     node: (&args.get(2).unwrap_or(&"".to_string())).clone(),
    // };

    let channel = Channel::from_static("http://localhost:50051")
        .connect()
        .await?;

    let mut client: MyServiceClient<Channel> = MyServiceClient::new(channel);

    let mut rl: rustyline::Editor<(), rustyline::history::FileHistory> = DefaultEditor::new()?;

    loop {
        let command = read_command(&mut rl);
        if command.is_none() {
            break;
        }
        let command = command.unwrap();
        let command = command.split(" ").collect::<Vec<&str>>();
        if command.len() == 0 || command[0] == "" {
            continue;
        }

        let mut args: Vec<String>= command
                .iter()
                .map(|&s| String::from(s))
                .collect::<Vec<String>>();
        

        match action_match(command[0], &mut client, &mut args).await {
            Ok(_) => {}
            Err(err) => {
                println!("{err}");
            }
        }
    }
    Ok(())
}
