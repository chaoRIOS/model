build-elf-parser:
	cd utils/elf-parser && cargo build --release
	rm -f utils/elfparser.so
	cp utils/elf-parser/target/release/libelfparser.so utils/elfparser.so