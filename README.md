# Performance model

Performance model built for PicoRio 2.0 is implemented with Python and Rust.

## Set up Rust environment
**Note**: Multiple Rust extensions will be conflicting. Make sure you have uninstalled any other Rust extensions.
```bash
## Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

## Install Rust components
rustup install nightly  
cargo +nightly install racer
cargo install --force rustfmt
cargo install --force rls

rustup component add rls-preview
rustup component add rust-analysis
rustup component add rust-src
```

Install `VS Code` extension `Rust` and set following configuration.

```json
{
    "rust-client.channel": "stable",
    "rust-client.rustupPath": "~/.cargo/bin/rustup",
    "editor.formatOnSave": true,
}
```
## Build Rust modules as dynamic link library

```bash
make build-[module-name]
```

Available modules:

|Module name|Python wrapper|Path|
|:-:|:-:|:-:|
|elfparser|`utils/elf_parser.py` |`utils/elf-parser/` |

