package main

import (
	"flag"
	"os"
	"testing"
)

func TestArgs(t *testing.T) {

	orArgs := os.Args

	flag.CommandLine = flag.NewFlagSet(orArgs[0], flag.ContinueOnError)
	os.Args = []string{"cmd", "-inSAN", "123"}
	setFlags()

	if InBumperSan != "123" {
		t.Error("InBumperSan not set by arg")
	}

	flag.CommandLine = flag.NewFlagSet(orArgs[0], flag.ContinueOnError)
	os.Args = []string{"cmd", "-out", "456"}
	setFlags()

	if OutCertDirectory != "456" {
		t.Error("Out path not set by arg")
	}

	flag.CommandLine = flag.NewFlagSet(orArgs[0], flag.ContinueOnError)
	os.Args = []string{"cmd", "-inSAN", "san1", "-out", "out2"}
	setFlags()

	if InBumperSan != "san1" {
		t.Error("InBumperSan not set by arg")
	}
	if OutCertDirectory != "out2" {
		t.Error("Out path not set by arg")
	}

	os.Args = orArgs
}
