# pychaoxingsigner😋

ChaoXing Signer.

Written in Python🐍

API inspired from [chaoxing-signin](https://github.com/cxOrz/chaoxing-signin/blob/main/apps/server/src/configs/api.ts).

Only supports locational signin for now. (Since u could do others on ur app isnt it 😘)

This script will run over ur courses and check if theres an activity 1 by 1, then sign it in. U could DIY `test.py` if u know a lil' 'bout Python🐍 :\)

## Run!!🏃‍♂️
U need to get a Python🐍, of course.
```bash
git clone https://github.com/Cosmic-Excalibur/pychaoxingsigner
cd pychaoxingsigner
python -r requirements.txt
```

Fill in `phone` (ur ℡, which is your account), `pwd` (ur password), `name` (ur name), `addr` (the address for locational signing in), `lonlat` (longitude & latitude) in `test.py`. Get the last two on [Baidu Map](https://api.map.baidu.com/lbsapi/getpoint/index.html).

Then run
```bash
python test.py
```
and `test.py` will automatically sign u in (locational) :\)

This should work on Termux, which allows your phone to sign you in.

## Todo✍️

- [ ] Selfie signin.
- [ ] Multithreading.
