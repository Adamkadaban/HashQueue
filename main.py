#!/bin/python3
from flask import Flask, request, jsonify
import os
import threading
import subprocess
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Dictionary to store cracked hashes
cracked_hashes = {}

potfile = '/root/.local/share/hashcat/hashcat.potfile'

def load_cracked_hashes():
    if os.path.exists(potfile):
        with open(potfile) as f:
            raw_hashes = f.readlines()
    else:
        return {}

    cracked_hashes = {}

    for h in raw_hashes:
        h = h.rstrip()
        h = h.split(':')
        cracked_hashes[h[0].split('*')[1]] = h[1]

    return cracked_hashes

def crack_hash(hash_to_crack):
    # Replace this command with your actual hashcat command
    # For example: subprocess.run(['hashcat', '-m', '0', hash_to_crack])
    # TODO: Deal with unknown hash mode. 
    print(f"Cracking hash: {hash_to_crack}")
    with open('/tmp/HashQueue.hash', 'w') as fout:
        fout.write(hash_to_crack)

    # os.popen('hashcat -m 22000 /tmp/HashQueue.hash /usr/share/wordlists/rockyou.txt')
    subprocess.Popen(['hashcat', '-m', '22000', '/tmp/HashQueue.hash', '/usr/share/wordlists/rockyou.txt'])
    return f"Hash cracked for {hash_to_crack}"


@app.route('/crackHash', methods=['POST'])
def crack_hash_endpoint():
    cracked_hashes = load_cracked_hashes()

    data = request.get_json()

    if 'hash' not in data:
        return jsonify({'error': 'Hash not provided'}), 400

    hash_to_crack = data['hash']

    # Check if the hash is already cracked

    if hash_to_crack.split('*')[5] in cracked_hashes:
        return jsonify({'result': f"Hash already cracked"})

    # Add the hash to the queue
    # hash_queue.put(hash_to_crack)
    crack_hash(hash_to_crack)

    return jsonify({'result': 'Hash added to the cracking queue'}), 200

@app.route('/crackPcap', methods=['POST'])
def crack_pcap_endpoint():
    print(request)
    if 'file' not in request.files:
        return jsonify({'error': 'File not provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error':'No file selected'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join('/opt/HashQueue/data', filename)
    file.save(filepath)
    print(f'[+] File saved to {filepath}')

    #os.popen(f'hcxpcapngtool -o /tmp/HashQueue.hash {filepath}')
    subprocess.call(['hcxpcapngtool', '-o', '/tmp/HashQueue.hash', filepath])

    print(f'Finished writing to /tmp/HashQueue.hash')

    if os.path.exists('/tmp/HashQueue.hash'):
        with open('/tmp/HashQueue.hash') as f:
            raw_hashes = [h.rstrip() for h in f.readlines()]

        for h in raw_hashes:
            print('Calling crack hash function')
            crack_hash(h)

        print('Removing /tmp/HashQueue.hash')
        #os.remove('/tmp/HashQueue.hash')

        return jsonify({'result': 'Hashes added to the cracking queue', 'hashes':raw_hashes}), 200
    else:
        return jsonify({'error': 'Hashes not found in pcap'}), 400

@app.route('/getCrackedHash', methods=['POST'])
def get_cracked_hash():
    cracked_hashes = load_cracked_hashes()

    # print(cracked_hashes)

    data = request.get_json()

    if 'hash' not in data:
        return jsonify({'error': 'Hash not provided'}), 400

    hash_to_check = data['hash']

    if hash_to_check.split('*')[5] not in cracked_hashes:
        return jsonify({'error': 'No request made to crack'}), 400
    elif cracked_hashes[hash_to_check.split('*')[5]] == '':
        return jsonify({'result': 'Unable to crack'}), 200

    return jsonify({'result': cracked_hashes[hash_to_check.split('*')[5]]}), 200

# Load cracked hashes from the potfile
cracked_hashes = load_cracked_hashes()

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
