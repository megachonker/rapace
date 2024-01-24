static PROTOFILE:&str = "protofile/api.proto";

fn main() {
    println!("cargo:rerun-if-changed={PROTOFILE}");
    tonic_build::compile_protos(PROTOFILE)
    .unwrap_or_else(|e| panic!("Failed to compile protos {:?}", e));
}