use std::env;
use tonic::{transport::Channel, Request};

// Importez les modules générés par protoc (protobuf compiler) pour Rust ici.
// Par exemple:
// mod api;
// use api::{api_client::ApiClient, Node, GetStatRequest, ...};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        println!("Usage: sudo ./client <action> <node> [additional_args]");
        return Ok(());
    }

    let action = &args[1];
    let node = &args[2];

    let channel = Channel::from_static("http://localhost:50051")
        .connect()
        .await?;

    let mut client = ApiClient::new(channel);

    match action.as_str() {
        "stat" => {
            let response = client
                .get_stat(Request::new(Node { node: node.clone() }))
                .await?;
            println!("Stat response: {:?}", response.into_inner().stat_info);
        },
        "reset" => {
            let response = client
                .reset(Request::new(Node { node: node.clone() }))
                .await?;
            println!("Reset response: {:?}", response.into_inner().message);
        },
        // Ajoutez les autres cas d'action ici, en suivant le même schéma.
        _ => {
            println!("Unknown action: {}", action);
        }
    }

    Ok(())
}
