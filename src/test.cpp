#include <fstream>
#include <jsoncpp/json/json.h>
#include <iostream>
#include <string>

int main (int argc, char *argv[]) {
	std::ifstream file("ex.json", std::ios::binary);
	Json::Value out;
	file >> out;

	std::cout << out << std::endl;
	return 0;
}
