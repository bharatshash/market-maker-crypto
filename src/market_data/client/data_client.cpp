//  Hello World client
#include <zmqpp/zmqpp.hpp>
#include <string>
#include <iostream>

using namespace std;

int main(int argc, char *argv[]) {
  const string endpoint = "tcp://localhost:5555";

  // initialize the 0MQ context
  zmqpp::context context;

  // generate a push socket
  zmqpp::socket_type type = zmqpp::socket_type::req;
  zmqpp::socket socket (context, type);

  // open the connection
  cout << "Connecting to python market data server…" << endl;
  socket.connect(endpoint);
  int request_nbr;
  for (request_nbr = 0; request_nbr != 10; request_nbr++) {
    // send data request
    cout << "Sending Market Data Request " << request_nbr <<"…" << endl;
    zmqpp::message request;
    // compose a message from a string and a number
    request << "Market Data Request";
    socket.send(request);
    string market_data;
    socket.receive(market_data);
    
    cout << "Ticker Update " << market_data << endl;
  }
}