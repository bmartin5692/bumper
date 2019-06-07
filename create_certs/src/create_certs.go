package main

import (
	"bufio"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha1"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"log"
	"math/big"
	"net"
	"os"
	"time"
)

func main() {

	make_CA()

	signCert()
}

func make_CA() {
	priv, _ := rsa.GenerateKey(rand.Reader, 2048)
	pub := &priv.PublicKey

	ca := &x509.Certificate{
		SerialNumber: big.NewInt(1653),
		Subject: pkix.Name{
			CommonName:   string("Bumper CA"),
			Organization: []string{"Bumper"},
		},
		NotBefore:             time.Now(),
		NotAfter:              time.Now().AddDate(10, 0, 0),
		SubjectKeyId:          bigIntHash(priv.N),
		AuthorityKeyId:        bigIntHash(priv.N),
		KeyUsage:              x509.KeyUsageCertSign | x509.KeyUsageCRLSign,
		ExtKeyUsage:           []x509.ExtKeyUsage{},
		IsCA:                  true,
		BasicConstraintsValid: true,
		MaxPathLen:            -1,
	}

	ca_b, err := x509.CreateCertificate(rand.Reader, ca, ca, pub, priv)
	if err != nil {
		log.Println("create ca failed", err)
		return
	}

	// Public key
	certOut, err := os.Create("ca.crt")
	if err != nil {
		log.Fatal("create ca.crt failed", err)
	}
	pem.Encode(certOut, &pem.Block{Type: "CERTIFICATE", Bytes: ca_b})
	certOut.Close()
	log.Print("ca.crt created\n")

	// Private key
	keyOut, err := os.OpenFile("ca.key", os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		log.Fatal("create ca.key failed", err)
	}
	pem.Encode(keyOut, &pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(priv)})
	keyOut.Close()
	log.Print("ca.key created\n")
}

func signCert() {

	// Load CA
	catls, err := tls.LoadX509KeyPair("ca.crt", "ca.key")
	if err != nil {
		log.Fatal("error loading ca cert", err)
	}

	ca, err := x509.ParseCertificate(catls.Certificate[0])
	if err != nil {
		log.Fatal("error parsing ca cert", err)
	}

	hostname, _ := os.Hostname()
	ifaces, err := net.Interfaces()
	var ips []net.IP
	// handle err
	for _, i := range ifaces {
		addrs, _ := i.Addrs()
		// handle err
		for _, addr := range addrs {
			var ip net.IP
			switch v := addr.(type) {
			case *net.IPNet:
				ip = v.IP
			case *net.IPAddr:
				ip = v.IP
			}
			ips = append(ips, ip)
			// process IP address
		}
	}
	ips = append(ips, net.ParseIP("127.0.0.1"))

	privateKey, _ := rsa.GenerateKey(rand.Reader, 2048)
	pubKey := &privateKey.PublicKey

	//DNS/SAN names for cert
	dnsNames := []string{hostname, "localhost"}
	//Read SANs from file
	if fileExists("Bumper_SAN.txt") {
		sans, err := readLines("Bumper_SAN.txt")
		if err != nil {
			log.Fatalf("readLines: %s", err)
		}
		dnsNames = append(dnsNames, sans...)
	}

	// Prepare certificate
	template := x509.Certificate{
		SerialNumber: big.NewInt(1658),
		Issuer:       ca.Subject,
		Subject: pkix.Name{
			CommonName:   "Bumper Server",
			Organization: []string{"Bumper"},
		},
		SubjectKeyId:          bigIntHash(privateKey.N),
		AuthorityKeyId:        ca.RawSubject,
		NotBefore:             time.Now(),
		NotAfter:              time.Now().AddDate(10, 0, 0),
		IsCA:                  false,
		BasicConstraintsValid: true,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageClientAuth, x509.ExtKeyUsageServerAuth},
		KeyUsage:              x509.KeyUsageDigitalSignature | x509.KeyUsageKeyEncipherment,
		DNSNames:              dnsNames,
		IPAddresses:           ips,
	}

	// Sign the certificate
	cert_b, err := x509.CreateCertificate(rand.Reader, &template, ca, pubKey, catls.PrivateKey)	

	// Public key
	certOut, err := os.Create("bumper.crt")
	if err != nil {
		log.Fatal("create bumper.crt failed", err)
	}
	pem.Encode(certOut, &pem.Block{Type: "CERTIFICATE", Bytes: cert_b})
	certOut.Close()
	log.Print("bumper.crt created\n")

	// Private key
	keyOut, err := os.OpenFile("bumper.key", os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		log.Fatal("create bumper.key failed", err)
	}
	pem.Encode(keyOut, &pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(privateKey)})
	keyOut.Close()
	log.Print("bumper.key created\n")
}

func bigIntHash(n *big.Int) []byte {
	h := sha1.New()
	h.Write(n.Bytes())
	return h.Sum(nil)
}

// readLines reads a whole file into memory
// and returns a slice of its lines.
func readLines(path string) ([]string, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	return lines, scanner.Err()
}

// fileExists checks if a file exists and is not a directory before we
// try using it to prevent further errors.
func fileExists(filename string) bool {
	info, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return !info.IsDir()
}
