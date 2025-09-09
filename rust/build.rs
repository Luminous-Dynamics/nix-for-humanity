//! Build script for PyO3 integration

fn main() {
    // Configure PyO3 build
    pyo3_build_config::add_extension_module_link_args();
    
    // Print cargo directives
    println!("cargo:rerun-if-changed=src/lib.rs");
    println!("cargo:rerun-if-changed=src/search.rs");
    println!("cargo:rerun-if-changed=src/cache.rs");
    println!("cargo:rerun-if-changed=src/parser.rs");
    println!("cargo:rerun-if-changed=src/optimizer.rs");
}