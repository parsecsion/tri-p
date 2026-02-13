import osmium
import sys

def convert(input_file, output_file):
    print(f"Converting {input_file} to {output_file}...")
    try:
        writer = osmium.SimpleWriter(output_file)
        reader = osmium.io.Reader(input_file)
        osmium.apply(reader, writer)
        writer.close()
        reader.close()
        print("Conversion successful.")
    except Exception as e:
        print(f"Error converting file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    convert(r"karachi.osm.pbf", r"karachi.osm")
