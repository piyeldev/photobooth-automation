import qrcode

# Ask the user for input
data = input("Enter the data to be encoded in the QR code: ")

# Generate the QR code
qr = qrcode.make(data)

# Save the QR code as an image file
qr.save("qr_code.png")

print("QR code generated and saved as qr_code.png.")
