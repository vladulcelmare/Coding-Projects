#include "GTree.h"
using namespace std;

bool cmp_int(const int a, const int b)
{
    return a > b;
}
bool cmp_str(char* a, char* b)
{
    return strcmp(a, b) < 0;
}

int main()
{
    cout << "=== INT TREE ===\n";
    Tree<int> t;

    t.add_node(10, nullptr);
    Node<int>* r = t.get_node(nullptr);

    t.add_node(5, r);
    t.add_node(20, r);
    t.add_node(15, r);

    cout << "Count: " << t.count(nullptr) << "\n";

    t.insert(r, 1, 99);
    t.sort(r, cmp_int);

    r->print();
    cout << "\n";

    cout << "\n=== CHAR* TREE ===\n";
    Tree<char*> ts;

    ts.add_node("root", nullptr);
    Node<char*>* rs = ts.get_node(nullptr);

    ts.add_node("banana", rs);
    ts.add_node("apple", rs);
    ts.add_node("cherry", rs);

    ts.sort(rs, cmp_str);

    rs->print();
    cout << "\n";

    return 0;
}