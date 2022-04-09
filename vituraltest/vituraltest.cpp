#include<iostream>
#include<memory>

class A{
public:
    virtual void Print(){
        std::cout << "A" << std::endl;
    }

};

class B: public A{
public:
    virtual void Print(){
        std::cout << "B" << std::endl;
    }
};

int main(){

    A* ptr  = new B;
    ptr->Print();
    (*ptr).Print();
    (static_cast<A>(*ptr)).Print();
    (static_cast<A*>(ptr))->Print();
    (reinterpret_cast<A*>(ptr))->Print();

    return 0;
}

