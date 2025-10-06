# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -g3 -Iinclude

# Source files
SRCS = main.cpp punto1.cpp punto2.cpp punto3.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Output executable
TARGET = main.exe

# Default rule: build, clean object files, run, and delete executable
all: $(TARGET) post-build run post-run

# Rule to build the target
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Rule to build object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Rule to remove object files after compilation
post-build:
	del /Q $(OBJS)

# Clean rule to delete all generated files
clean:
	del /Q $(OBJS) $(TARGET)

# Run rule
run:
	$(TARGET)

# Rule to delete the executable after running
post-run:
	del /Q $(TARGET)