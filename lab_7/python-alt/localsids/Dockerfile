FROM python:3.8.10
WORKDIR /demo-processors/l3vpn
COPY . /demo-processors/l3vpn
#RUN pip3 install -r /demo-processors/l3vpn/requirements.txt
RUN pip3 install -r /demo-processors/l3vpn/requirements.txt --proxy=proxy.esl.cisco.com:8080
CMD ["python3.6","create_l3vpn_topology.py"]
