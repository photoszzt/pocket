#include <iostream>
#include <random>

std::string random_string(std::string::size_type length)
{
    static auto& chrs = "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    thread_local static std::mt19937 rg{std::random_device{}()};
    thread_local static std::uniform_int_distribution<std::string::size_type> pick(0, sizeof(chrs) - 2);

    std::string s;

    s.reserve(length);

    while(length--)
        s += chrs[pick(rg)];

    return s;
}

#include "cpppocket_dispatcher.h"
int main(int argc, char *argv[])
{
    string address = "10.1.0.10";
    int port = 9070;
    CPPPocketDispatcher dispatcher;
    if (dispatcher.Initialize(address, port))
    {
        std::cout << "Cannot initialize dispatcher" << endl;
        return 01;
    }
    std::vector<std::string> names;
    for (int i = 0; i < 1000; i++)
    {
        std::string tmp = random_string(4);
        tmp.append(std::to_string(i));
        names.push_back(tmp);
    }
    unsigned int size = 1024 * 1024;
    string data;
    data.reserve(size);
    uint8_t counter = 0;
    for (unsigned int i = 0; i < size; i++)
    {
        data.push_back(counter);
        if (counter == 127)
        {
            counter = 0;
        }
        counter += 1;
    }
    int res = -1;
    for (std::string n : names)
    {
        res = dispatcher.PutBuffer(data.data(), n, false);
    }
    for (std::string n : names)
    {
        auto object = dispatcher.GetBufferBytes(n);
    }
}
