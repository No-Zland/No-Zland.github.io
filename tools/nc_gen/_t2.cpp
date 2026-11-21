#include <cstdio>
#include <vector>
#include <algorithm>
#include <functional>
#include <cstring>
#include <string>
int main(){std::vector<int> v{3,1}; std::sort(v.begin(),v.end(),std::greater<int>()); printf("%d\n",v[0]);}
