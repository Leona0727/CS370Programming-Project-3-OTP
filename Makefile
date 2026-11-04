
.PHONY: all generate-qr get-otp clean

all:
	python3 -m pip install "qrcode[pil]"

generate-qr:
	python3 submission.py --generate-qr

get-otp:
	python3 submission.py --get-otp

clean:
	rm -f otp_qr.jpg
