#include <cstring>
#include <iostream>

template <class T>
class Tree;

template <class T>
class Node
{
    //template <class U> friend class Tree;
    friend class Tree<T>;

    T information;
    int count = 0;
    Node<T>* parent = nullptr;
    Node<T>** list = nullptr;

    public:
        Node() = default;

        Node(T x) : information(x) {};

        const int get_count() const
        {
            return count; 
        };

        const T& get_info() const
        {
            return information;
        };

        void print() const
        {
            std::cout << "Node info: " << information << "\n";
            std::cout << "Children: ";
            for (int i = 0; i < count; ++i)
                std::cout << list[i]->information << " ";
            std::cout << "\n";
        };

        ~Node()
        {
            for (int i = 0; i < count; ++i)
                delete list[i];
            delete[] list;
        };
};

template <>
class Node<char*>
{
    friend class Tree<char*>;

    char* information = nullptr;
    int count = 0;
    Node<char*>* parent = nullptr;
    Node<char*>** list = nullptr;

    public:
        Node() : Node("") {};

        Node(const char* x)
        {
            int len = strlen(x);
            information = new char[len + 1];
            strcpy(information, x);
        };

        const int get_count() const
        {
            return count; 
        };
    
        const char* get_info() const
        {
            return information; 
        };

        void print() const
        {
            std::cout << "Node info: " << information << "\n";
            std::cout << "Children: ";
            for (int i = 0; i < count; ++i)
                std::cout << list[i]->information << " ";
            std::cout << "\n";
        };

        ~Node()
        {
            delete[] information;
            for (int i = 0; i < count; ++i)
                delete list[i];
            delete[] list;
        };
};

template <class T>
class Tree
{
    Node<T>* root = nullptr;

    public:
    Tree() = default;
    
    ~Tree() 
    { 
        delete root; 
    };

    void add_node(T x, Node<T>* parent)
    {
        Node<T>* newNode = new Node<T>(x);

        if (parent == nullptr)
        {
            delete root;
            root = newNode;
            root->parent = nullptr;
            return;
        }

        Node<T>** new_list = new Node<T>*[parent->count + 1];

        for (int i = 0; i < parent->count; ++i)
            new_list[i] = parent->list[i];

        new_list[parent->count] = newNode;
        newNode->parent = parent;

        delete[] parent->list;
        parent->list = new_list;
        parent->count++;
    };

    Node<T>* find(bool (*cmp)(const T&, const T&), const T& value, Node<T>* current)
    {
        if (current == nullptr)
            current = root;
        
        if (current == nullptr)
            return nullptr;

        if (cmp(current->information, value))
            return current;

        for (int i = 0; i < current->count; ++i)
        {
            Node<T>* res = find(cmp, value, current->list[i]);
            if (res) return res;
        }
        return nullptr;
    };

    Node<T>* get_node(Node<T>* parent) const
    {
        if (parent == nullptr)
            return root;

        if (parent->count == 0)
            return nullptr;

        return parent->list[0]; 
    };

    void delete_node(Node<T>* node)
    {
        if (node == nullptr)
            return;

        if (node == root)
        {
            delete root;
            root = nullptr;
            return;
        }

        Node<T>* p = node->parent;
        if (p == nullptr)
            return;

        int pos = -1;
        for (int i = 0; i < p->count; ++i)
        {
            if (p->list[i] == node)
            {
                pos = i;
                break;
            }
        }
        if (pos == -1)
            return;

        delete node;

        for (int i = pos; i < p->count - 1; ++i)
            p->list[i] = p->list[i + 1];

        p->count--;
    };

    void insert(Node<T>* parent, int index, const T& x)
    {
        if (parent == nullptr)
            return;
        
        Node<T>** new_list = new Node<T>*[parent->count + 1];

        for (int i = 0; i < index; ++i)
            new_list[i] = parent->list[i];

        new_list[index] = new Node<T>(x);
        new_list[index]->parent = parent;

        for (int i = index; i < parent->count; ++i)
            new_list[i + 1] = parent->list[i];

        delete[] parent->list;
        parent->list = new_list;
        parent->count++;
    };

    void sort(Node<T>* parent,bool (*cmp)(T, T))
    {
        if (parent == nullptr || parent->count <= 1)
            return;

        for (int i = 0; i < parent->count - 1; ++i)
        {
            for (int j = i + 1; j < parent->count; ++j)
            {
                if (cmp(parent->list[j]->information, parent->list[i]->information))
                {
                    Node<T>* temp = parent->list[i];
                    parent->list[i] = parent->list[j];
                    parent->list[j] = temp;
                }
            }
        }
    };

    int count(Node<T>* parent) const
    {
        if (parent == nullptr)
            parent = root;
            
        if (parent == nullptr)
            return 0;

        int total = parent->count;
        for (int i = 0; i < parent->count; ++i)
            total += count(parent->list[i]);

        return total;
    };
};