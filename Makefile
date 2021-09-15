build-decoder:
	cd utils/decoder && cargo build --release
	rm -f utils/rustdecoder.so
	cp utils/decoder/target/release/librustdecoder.so utils/rustdecoder.so

build-elfparser:
	cd utils/elf-parser && cargo build --release
	rm -f utils/elfparser.so
	cp utils/elf-parser/target/release/libelfparser.so utils/elfparser.so