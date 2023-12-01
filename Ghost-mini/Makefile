./bin/mini-ghost: ./obj/main.o ./obj/data_extractor.o ./obj/network_manager.o
	gcc -static -o ./bin/mini-ghost ./obj/network_manager.o ./obj/data_extractor.o ./obj/main.o

./obj/main.o: ./src/main.c
	gcc -c ./src/main.c -o ./obj/main.o

./obj/data_extractor.o: ./src/data_extractor.c
	gcc -c ./src/data_extractor.c -o ./obj/data_extractor.o

./obj/network_manager.o: ./src/network_manager.c
	gcc -c ./src/network_manager.c -o ./obj/network_manager.o

cleanup:
	rm ./obj/main.o
	rm ./obj/data_extractor.o
	rm ./obj/network_manager.o
	rm ./bin/mini-ghost