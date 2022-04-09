#include <stdio.h>

class student
{
	public:
		    student() {}
		        ~student() {}
};

class bachelor
{
	public:
		    bachelor() {}
		        ~bachelor() {}
};
class studentHolder
{
	public:
		    studentHolder()
			        {

					    }

        protected:
		        virtual ~studentHolder();


	private:
			    student st;
			    int fd;
};

class bachelorHolder : public studentHolder
{
	public:
		    bachelorHolder()
			            : studentHolder()
				          {

						      }

		        ~bachelorHolder() override
				    {

					        }

	private:
			    bachelor bcl;
};
