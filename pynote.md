\*\*\*Mặt khác, key có thể được thêm vào hoặc loại bỏ bằng cách convert view trả về bởi keys() thành một object list:

> > > prices = {'apple': 0.40, 'orange': 0.35, 'banana': 0.25}
> > > for key in list(prices.keys()): # Use a list instead of a view
> > > ... if key == 'orange':
> > > ... del prices[key] # Delete a key from prices
> > > ...
> > > prices
> > > {'apple': 0.4, 'banana': 0.25}

Cuối cùng, nếu bạn muốn loại bỏ một key của prices sử dụng .keys() một cách trực tiếp, Python sẽ raise lên RuntimeError để nhắc nhở bạn rằng kích thước dict bị thay đổi trong khi lặp:

> > > # Python 3. dict.keys() returns a view object, not a list
> > >
> > > prices = {'apple': 0.40, 'orange': 0.35, 'banana': 0.25}
> > > for key in prices.keys():
> > > ... if key == 'orange':
> > > ... del prices[key]
> > > ...
> > > Traceback (most recent call last):
> > > File "<input>", line 1, in <module>

    for key in prices.keys():

RuntimeError: dictionary changed size during iteration

\*\*\*với các đối tượng immutable, việc gán cho nhau là một việc rất dễ hiểu, bởi khi thay đổi giá trị thì định danh của nó cũng thay đổi theo.
Tuy nhiên, với đối tượng mutable, mọi việc rắc rối hơn rất nhiều. Việc gán biến lẫn nhau chỉ đơn giản là nói rằng biến đó sẽ trỏ đến cùng một vùng nhớ, và giá trị được lưu trong vùng nhớ đó hoàn toàn có thể thay đổi mà không thay đổi định danh.

Trong Python, những đối tượng thuộc loại sau là mutable:
list
dict
set
bytearray
Các class được định nghĩa bởi code (mặc định)

Các đối tượng thuộc loại sau là immutable:
int
float
decimal
complex
bool
string
tuple
range
frozenset
bytes

\*\*\*Transaction
https://kipalog.com/posts/DB-Transaction
Atomic Nguyên tử
Consistancy Tính nhất quán
Isolation
Durability
