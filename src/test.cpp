#include <zmqpp/zmqpp.hpp>
#include <iostream>

int main() {
    zmqpp::context ctx;
    zmqpp::socket pub(ctx, zmqpp::socket_type::pub);
    pub.bind("tcp://127.0.0.1:5555");

    zmqpp::message msg;
    msg << "Hello ZeroMQ";
    pub.send(msg);

    std::cout << "Message sent!" << std::endl;
    return 0;
}
