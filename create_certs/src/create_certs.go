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
	"flag"
	"fmt"
	"log"
	"math/big"
	"net"
	"os"
	"path/filepath"
	"time"
)

var InBumperSan string
var OutCertDirectory string

func setFlags() {

	exePath, _ := os.Executable()
	currentDir, _ := os.Getwd()

	//certPath will be current working directory by defaultß
	certPath, err := filepath.Abs(currentDir)
	if err != nil {
		log.Printf("Error: %v", err)
	}

	//sanPath will be exe path /Bumper_SAN.txt by default
	sanPath, err := filepath.Abs(filepath.Join(exePath, "..", "/Bumper_SAN.txt"))
	if err != nil {
		log.Printf("Error: %v", err)
	}

	flag.StringVar(&InBumperSan, "inSAN", sanPath, "Input file containing a list of Subject Alternate Names (line separated)")
	flag.StringVar(&OutCertDirectory, "out", certPath, "Directory to output certificates to")

	flag.Parse()

}
func main() {

	setFlags()

	fmt.Printf("-------- Create_Certs --------\n")

	//get absolute path
	outCertDirectory, _ := filepath.Abs(OutCertDirectory)
	dexists, isdfile := pathExistsType(outCertDirectory)
	if !dexists {
		log.Fatalf("Certs directory doesn't exist: %v", outCertDirectory)
	}
	if isdfile {
		log.Fatalf("Certs directory is a file, not a directory: %v", outCertDirectory)
	}

	//get absolute path
	inBumperSan, _ := filepath.Abs(InBumperSan)
	bexists, isbfile := pathExistsType(inBumperSan)
	if !bexists {
		log.Printf("Bumper SAN doesn't exist, certificate won't contain Subject Alternate Names: %v\n", inBumperSan)
		inBumperSan = ""
	}
	if bexists && !isbfile {
		log.Printf("Bumper SAN is a directory instead of file, certificate won't contain Subject Alternate Names: %v\n", inBumperSan)
		inBumperSan = ""
	}

	fmt.Printf("-------- Starting Certificate Creation --------\n")
	fmt.Printf("Options: \n Output Directory: %v\n Input SAN List: %v\n", outCertDirectory, inBumperSan)

	make_CA(outCertDirectory)
	signCert(outCertDirectory, inBumperSan)

	fmt.Printf("-------- Certificate Creation Complete --------\n")
}

func make_CA(outCertDirectory string) {

	fmt.Printf("-------- Creating CA Cert --------\n")
	priv, _ := rsa.GenerateKey(rand.Reader, 2048)
	pub := &priv.PublicKey

	ca := &x509.Certificate{
		SerialNumber: big.NewInt(1653),
		Subject: pkix.Name{
			CommonName:   string("Bumper CA"),
			Organization: []string{"Bumper"},
		},
		NotBefore:             time.Now(),
		NotAfter:              time.Now().AddDate(2, 0, 0),
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
		log.Fatalf("Create ca failed: %v", err)
	}

	// Public key
	certOut, err := os.Create(filepath.Join(outCertDirectory, "ca.crt"))
	if err != nil {
		log.Fatalf("Create ca.crt failed: %v", err)
	}
	pem.Encode(certOut, &pem.Block{Type: "CERTIFICATE", Bytes: ca_b})
	certOut.Close()
	log.Printf("ca.crt created at %v\n", filepath.Join(outCertDirectory, "ca.crt"))

	// Private key
	keyOut, err := os.OpenFile(filepath.Join(outCertDirectory, "ca.key"), os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		log.Fatalf("Create ca.key failed: %v", err)
	}
	pem.Encode(keyOut, &pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(priv)})
	keyOut.Close()
	log.Printf("ca.key created at %v\n", filepath.Join(outCertDirectory, "ca.key"))
}

func signCert(outCertDirectory string, inBumperSan string) {

	fmt.Printf("-------- Creating Server Cert --------\n")
	// Load CA
	catls, err := tls.LoadX509KeyPair(filepath.Join(outCertDirectory, "ca.crt"), filepath.Join(outCertDirectory, "ca.key"))
	if err != nil {
		log.Fatalf("Error loading ca cert: %v", err)
	}

	ca, err := x509.ParseCertificate(catls.Certificate[0])
	if err != nil {
		log.Fatalf("Error parsing ca cert: %v", err)
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
	//get absolute path

	bexists, isbfile := pathExistsType(inBumperSan)
	if !bexists {
		log.Print("Bumper SAN doesn't exist, certificate won't contain Subject Alternate Names")
	}
	if bexists && !isbfile {
		log.Print("Bumper SAN is a directory instead of file, certificate won't contain Subject Alternate Names")
	}
	if bexists && isbfile {
		sans, err := readLines(inBumperSan)
		if err != nil {
			log.Printf("Error reading %v certificates will be created without Subject Alternate Names: %v", inBumperSan, err)
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
		NotAfter:              time.Now().AddDate(2, 0, 0),
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
	certOut, err := os.Create(filepath.Join(outCertDirectory, "bumper.crt"))
	if err != nil {
		log.Fatalf("Create bumper.crt failed: %v", err)
	}
	pem.Encode(certOut, &pem.Block{Type: "CERTIFICATE", Bytes: cert_b})
	certOut.Close()
	log.Printf("bumper.crt created at %v\n", filepath.Join(outCertDirectory, "bumper.crt"))

	// Private key
	keyOut, err := os.OpenFile(filepath.Join(outCertDirectory, "bumper.key"), os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		log.Fatalf("create bumper.key failed: %v", err)
	}
	pem.Encode(keyOut, &pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(privateKey)})
	keyOut.Close()
	log.Printf("bumper.key created at %v\n", filepath.Join(outCertDirectory, "bumper.key"))
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

// pathexistsType checks if a path exists and is a file or directory
func pathExistsType(filename string) (exists bool, isfile bool) {
	info, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false, false
	}
	return true, !info.IsDir()
}
