from flask import Flask, request, jsonify
import subprocess
import os
from queue import Queue

app = Flask(__name__)

# Queue to manage hash cracking requests
hash_queue = Queue()

# Dictionary to store cracked hashes
cracked_hashes = {}

potfile = '/root/.hashcat/hashcat.potfile'

# Load cracked hashes from the potfile
cracked_hashes = load_cracked_hashes()

def load_cracked_hashes():
    if os.path.exists(potfile):
        with open(potfile) as f:
            raw_hashes = f.readlines()
    else:
        return {}

    cracked_hashes = {}

    for hash in raw_hashes:
        hash = hash.rstrip()
        hash = hash.split(':')
        cracked_hashes[hash[0]] = hash[1]

    return cracked_hashes

def update_cracked_hashes(hash, result):
    cracked_hashes[hash] = result

def crack_hash(hash_to_crack):
    # Replace this command with your actual hashcat command
    # For example: subprocess.run(['hashcat', '-m', '0', hash_to_crack])
	# TODO: Deal with unknown hash mode. 
    print(f"Cracking hash: {hash_to_crack}")
    with open('/tmp/HashQueue.hash', 'w') as fout:
        fout.write(hash_to_crack)
    subprocess.run(['hashcat', '-m', '22000', '/tmp/HashQueue.hash', '/usr/share/wordlists/rockyou.txt'])
    return f"Hash cracked for {hash_to_crack}"


@app.route('/crackHash', methods=['POST'])
def crack_hash_endpoint():
    data = request.get_json()

    if 'hash' not in data:
        return jsonify({'error': 'Hash not provided'}), 400

    hash_to_crack = data['hash']

    # Check if the hash is already cracked

    if hash_to_crack in cracked_hashes:
        return jsonify({'result': f"Hash already cracked: {cracked_hashes[hash_to_crack]}"})

    # Add the hash to the queue
    hash_queue.put(hash_to_crack)

    return jsonify({'result': 'Hash added to the cracking queue'})

@app.route('/crackPcap', methods=['PUT'])
def crack_pcap_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'File not provided'}), 400

    file = request.files['file']

    if file.filename = '':
        return jsonify({'error':'No file selected'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join('/opt/HashQueue/data', filename)
    file.save(path)

    subprocess.run(['hcxpcapngtool', '-o', '/tmp/HashQueue.hash', filepath])

    if os.path.exists('/tmp/HashQueue.hash'):
        with open('/tmp/HashQueue.hash') as f:
            raw_hashes = [h.rstrip() for h in f.readlines()]

        for hash in raw_hashes:
            crack_hash(hash)

        return jsonify({'result': 'Hashes added to the cracking queue'}), 200
    else:
        return jsonify({'error': 'Hashes not found in pcap'}), 400


def process_queue():
    while not hash_queue.empty():
        hash_to_crack = hash_queue.get()
        result = crack_hash(hash_to_crack)
        update_cracked_hashes(hash_to_crack, result)

if __name__ == '__main__':
    # Run the queue processing in the background
    import threading
    threading.Thread(target=process_queue, daemon=True).start()

    app.run(debug=True)
