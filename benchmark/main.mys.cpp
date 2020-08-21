#include <iostream>
#include <cassert>
#include <cstdint>
#include <tuple>
#include <utility>
#include <vector>
#include <string>
#include <iterator>
#include <algorithm>
#include <memory>
#include <numeric>
#include <boost/algorithm/hex.hpp>

//namespace binascii {
//    std::string unhexlify(std::string data);
//}

//template <typename T> auto crc_srec(Thexstr hexstr) {
//    auto crc;
//    crc = sum(binascii::unhexlify(hexstr))
//    crc &= 0xff
//    crc ^= 0xff
//
//    return crc


auto s1_p = std::make_shared<std::string>("0159");
auto s2_p = std::make_shared<std::string>("268");
auto s3_p = std::make_shared<std::string>("37");
auto s4_p = std::make_shared<std::string>("S214400254040000001000000001000000474E550056");
auto s5_p = std::make_shared<std::string>("S2144002640000000002000000060000001800000025");
auto s6_p = std::make_shared<std::string>("S214400274040000001400000003000000474E550030");
auto s7_p = std::make_shared<std::string>("S214400284BB192DAB28022B1866A9BC5BBD1359DBE2");
auto s8_p = std::make_shared<std::string>("S2084002942F4F95AF5F");

static std::tuple<std::string, int, int, std::shared_ptr<std::string>>
unpack_srec(std::shared_ptr<std::string> record_p)
{
    if (record_p->size() < 6) {
        throw "record_p->size() < 6";
    }

    if (record_p->at(0) != 'S') {
        throw "record_p->at(0) != 'S'";
    }

    auto value_p = std::make_shared<std::string>();
    boost::algorithm::unhex(record_p->begin() + 2,
                            record_p->end(),
                            std::back_inserter(*value_p));
    auto size = value_p->at(0);

    if ((size_t)size != value_p->size() - 1) {
        throw "size != value.size() - 1";
    }

    auto type = record_p->at(1);
    auto width = 0;
    
    if (s1_p->find(type) != std::string::npos) {
        width = 2;
    } else if (s2_p->find(type) != std::string::npos) {
        width = 3;
    } else if (s3_p->find(type) != std::string::npos) {
        width = 4;
    } else {
        throw "type";
    }

    auto address = 1;
    auto data_offset = (1 + width);
    auto data_p = std::make_shared<std::string>(
                      std::string(value_p->begin() + data_offset, value_p->end() - 1));

    return std::make_tuple(std::string(""), address, data_p->size(), data_p);
}

//     address = int.from_bytes(value[1:data_offset], byteorder='big')
//     actual_crc = value[-1]
//     expected_crc = crc_srec(record[2:-2])
//
//     if actual_crc != expected_crc:
//         raise Error()
//
//     return (type_, address, len(data), data)

static int run(void)
{
    std::vector<std::shared_ptr<std::string>> records = {
        s4_p, s5_p, s6_p, s7_p, s8_p
    };

    std::vector<std::tuple<std::string, int, int, std::shared_ptr<std::string>>> result;

    for (auto& item: records) {
        result.push_back(unpack_srec(item));
    }

    std::vector<int> tmp;
    std::transform(result.begin(),
                   result.end(),
                   std::back_inserter(tmp),
                   [](auto& item) {
                       return std::get<2>(item);
                   });

    return std::accumulate(tmp.begin(), tmp.end(), decltype(tmp)::value_type(0));
}

int main()
{
    auto value = 0;

    for (auto i = 0; i < 10000; i++) {
        value += run();
    }

    std::cout << "Result: " << value << std::endl;

    return (0);
}
