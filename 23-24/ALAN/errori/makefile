# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -g3

# Source files
SRCS = 1esercizio.cpp 2esercizio.cpp 3esercizio.cpp

# Executable names
EXES = 1esercizio.exe 2esercizio.exe 3esercizio.exe

# Output file for results
OUTPUT_FILE = results.txt

# Default rule: clean previous results, build each file, and save output
all: clean $(EXES) save_output

# Rule to build each executable
%.exe: %.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

# Rule to save output from each executable to OUTPUT_FILE
save_output:
	@echo Esercizio 1:" > $(OUTPUT_FILE)
	1esercizio.exe >> $(OUTPUT_FILE)
	@echo Esercizio 2:" >> $(OUTPUT_FILE)
	2esercizio.exe >> $(OUTPUT_FILE)
	@echo "Esercizio 3:" >> $(OUTPUT_FILE)
	3esercizio.exe >> $(OUTPUT_FILE)

# Clean rule to delete generated files
clean:
	del /Q $(EXES) $(OUTPUT_FILE)

post-run:
	del /Q $(TARGET)
