use core::fmt;
use serde::{Deserialize, Serialize};
use std::io::Write;
use std::{
    borrow::Borrow,
    collections::HashMap,
    fmt::{write, Debug, Display},
    fs::{self, File},
    io,
    process::Command,
};

#[derive(Serialize, Deserialize, Debug, PartialEq, Eq, Hash)]
#[allow(non_snake_case)]
struct Node {
    id: String,
    role: Option<String>,
    isHost: Option<bool>,
    loopback: Option<String>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Link {
    node1: String,
    port1: u16,
    ip1: Option<String>,
    node2: String,
    port2: u16,
    ip2: Option<String>,
    weight: u16,
}

impl fmt::Display for Link {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "   {}_port_{} -- {}_port_{} [label =\"{}\"]",
            self.node1, self.port1, self.node2, self.port2, self.weight
        )
    }
}

#[derive(Serialize, Deserialize, Debug)]
struct Graphformat {
    nodes: Vec<Node>,
    links: Vec<Link>,
}

struct GraphCluster {
    node: GraphNode,
    ports: Vec<GraphPort>,
}

impl fmt::Display for GraphCluster {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            r#"
    subgraph Cluster_{} {{
        {}"#,
            self.node.id, self.node.id
        )
        .unwrap();
        for port in &self.ports {
            write!(
                f,
                r#"
        {}_port_{}"#,
                self.node.id, port.port_number
            )
            .unwrap();
        }

        write!(
            f,
            r#"
    }}
    "#
        )
    }
}

#[derive(Debug, Clone)]
struct GraphNode {
    id: String,
    role: Role,
    address: Option<String>,
}

impl From<Node> for GraphNode {
    fn from(value: Node) -> Self {
        let mut role;
        if let Some(rr) = value.role {
            role = match rr.as_str() {
                "Firewall" => Role::Firewall,
                "Router" => Role::Router,
                "LoadBalancer" => Role::LoadBalancer,
                "Repeater" => Role::Repeter,
                _ => Role::ERR,
            };
        } else {
            role = Role::Empty;
            if value.id.contains("h") {
                role = Role::User
            }
        }

        GraphNode {
            id: value.id,
            role,
            address: value.loopback,
        }
    }
}

#[derive(Debug, Clone)]
enum Role {
    User,
    Firewall,
    Router,
    LoadBalancer,
    Repeter,
    Empty,
    ERR,
}

fn choosecolor(role: &Role) -> String {
    return match role {
        Role::User => "bae1ff",
        Role::Firewall => "ffb3ba",
        Role::Router => "ffdfba",
        Role::LoadBalancer => "ffffba",
        Role::Repeter => "baffc9",
        Role::Empty => "D3D3D3",
        Role::ERR => "FFFFFF",
    }
    .to_string();
}

fn displayrole(role: Role) -> String {
    return match role {
        Role::User => "User",
        Role::Firewall => "Firewall",
        Role::Router => "Router",
        Role::LoadBalancer => "LoadBalancer",
        Role::Repeter => "Repeter",
        Role::Empty => "Empty",
        Role::ERR => "Error parsing role",
    }
    .to_string();
}

impl fmt::Display for GraphNode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "    {} [label = \"node: {}", self.id, self.id).unwrap();

        let rolename = displayrole(self.role.clone());
        write!(f, " | {rolename}").unwrap();

        if let Some(ipaddres) = self.address.clone() {
            write!(f, " | {}", ipaddres).unwrap();
        }

        //color
        write!(
            f,
            " \"style=filled fillcolor=\"#{}\"",
            choosecolor(&self.role)
        )
        .unwrap();

        write!(f, " shape = \"record\"]")
    }
}

#[derive(Clone)]
pub struct GraphPort {
    dady: String, //pour pas ce faire chier a ce trimbaler avec un context
    port_number: u16,
    ip_address: Option<String>,
}

impl fmt::Display for GraphPort {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "    {}_port_{} [label = \"port: {} ",
            self.dady, self.port_number, self.port_number
        )
        .unwrap();
        if let Some(addresse) = self.ip_address.clone() {
            write!(f, "| {}", addresse).unwrap();
        }
        write!(f, " \"style=filled fillcolor=\"#{}\"", "ffdbf1").unwrap();
        write!(f, " shape = \"record\"]")
    }
}

impl GraphPort {
    fn from(link: Link) -> (GraphPort, GraphPort) {
        (
            GraphPort {
                dady: link.node1,
                ip_address: link.ip1,
                port_number: link.port1,
            },
            GraphPort {
                dady: link.node2,
                ip_address: link.ip2,
                port_number: link.port2,
            },
        )
    }
}

fn main() {
    let data = fs::read_to_string("./graph.json").expect("failed load the file");
    let parsed: Graphformat = serde_json::from_str(&data).expect("failed to parse the json");

    let mut node_list_org = vec![];
    let mut port_list_org = vec![];
    let mut cluster_list = HashMap::new();

    //gen node label
    for parsed_node in parsed.nodes {
        node_list_org.push(GraphNode::from(parsed_node));
    }
    //gen port label
    for port in &parsed.links {
        let (p1, p2) = GraphPort::from(port.clone());
        port_list_org.push(p1);
        port_list_org.push(p2);
    }

    //gen all graph cluster
    //consume list org and fill ref cluster
    for node in node_list_org {
        let node_id = node.id.clone();
        let cluster = GraphCluster {
            node: node,
            ports: vec![], //fill it after
        };
        cluster_list.insert(node_id.clone(), cluster);
    }
    //fill porst for all graph cluster
    for port in port_list_org {
        //find the coresponding cluster to port
        cluster_list
            .get_mut(&port.dady)
            .expect("port appartenant pas a une node qui n'es dans aucun cluster")
            .ports
            .push(port);
    }

    //clean empty subgraf
    cluster_list.retain(|_key, cluster| !cluster.ports.is_empty());

    yiyip(cluster_list, parsed.links).expect("erreur entrée sortie");
    Command::new("dot")
        .args(["-Tpng", "/tmp/boykisser.txt", "-o", "/tmp/boykisser.png"])
        .output()
        .expect("imposible de run la cmd dot");
    Command::new("xdg-open")
        .arg("/tmp/boykisser.png")
        .output();
        
}

fn yiyip(cluster_list: HashMap<String, GraphCluster>, link_list: Vec<Link>) -> io::Result<()> {
    let mut outfile = File::create("/tmp/boykisser.txt")?;

    let header = r#"
graph G {
    graph [
        rankdir = "LR"
    ];
    "#;
    println!("{header}");
    writeln!(outfile, "{header}")?;

    //print all cluster
    for cluster in cluster_list.values() {
        println!("{cluster}");
        writeln!(outfile, "{cluster}")?;
        println!("{}", cluster.node);
        writeln!(outfile, "{}", cluster.node)?;
        for port in &cluster.ports {
            println!("{port}");
            writeln!(outfile, "{port}")?;
        }
    }
    println!("");
    writeln!(outfile, "")?;

    //print all link
    for link in link_list {
        println!("{link}");
        writeln!(outfile, "{link}")?;
    }

    println!("}}");
    write!(outfile, "}}")
}
