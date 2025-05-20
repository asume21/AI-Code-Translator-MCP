# Test Code Samples for AI Code Translator

## Python

### Simple Function
```python
def factorial(n):
    """Calculate the factorial of a number recursively."""
    if n <= 1:
        return 1
    return n * factorial(n-1)

# Test the function
result = factorial(5)
print(f"Factorial of 5 is {result}")
```

### Class Definition
```python
class BankAccount:
    """A simple bank account class with deposit and withdrawal functionality."""
    
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.transactions = []
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.transactions.append(("deposit", amount))
        return self.balance
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.transactions.append(("withdrawal", amount))
        return self.balance
    
    def get_transaction_history(self):
        return self.transactions
    
    def __str__(self):
        return f"Account owner: {self.owner}\nBalance: ${self.balance}"

# Create an account and perform operations
account = BankAccount("John Doe", 1000)
account.deposit(500)
account.withdraw(200)
print(account)
print(f"Transaction history: {account.get_transaction_history()}")
```

### Algorithm Implementation (Quicksort)
```python
def quicksort(arr):
    """
    Implement the quicksort algorithm to sort an array.
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# Test the algorithm
unsorted_list = [3, 6, 8, 10, 1, 2, 1, 7]
sorted_list = quicksort(unsorted_list)
print(f"Unsorted: {unsorted_list}")
print(f"Sorted: {sorted_list}")
```

### Code with Vulnerabilities
```python
import os
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # SQL Injection vulnerability
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name LIKE '%{query}%'")
    results = cursor.fetchall()
    
    # Command Injection vulnerability
    os.system(f"echo Search results for: {query} >> log.txt")
    
    # XSS vulnerability
    template = f'''
    <h1>Search Results for: {query}</h1>
    <ul>
        {% for result in results %}
        <li>{{ result }}</li>
        {% endfor %}
    </ul>
    '''
    
    # Template Injection vulnerability
    return render_template_string(template, results=results)

if __name__ == '__main__':
    app.run(debug=True)
```

## JavaScript

### Simple Function
```javascript
/**
 * Calculate the factorial of a number recursively.
 * @param {number} n - The input number
 * @return {number} The factorial of n
 */
function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// Test the function
const result = factorial(5);
console.log(`Factorial of 5 is ${result}`);
```

### Class Definition
```javascript
/**
 * A simple bank account class with deposit and withdrawal functionality.
 */
class BankAccount {
    /**
     * Create a new bank account
     * @param {string} owner - The account owner's name
     * @param {number} balance - Initial balance (default 0)
     */
    constructor(owner, balance = 0) {
        this.owner = owner;
        this.balance = balance;
        this.transactions = [];
    }
    
    /**
     * Deposit money into the account
     * @param {number} amount - Amount to deposit
     * @return {number} New balance
     */
    deposit(amount) {
        if (amount <= 0) {
            throw new Error("Deposit amount must be positive");
        }
        this.balance += amount;
        this.transactions.push(["deposit", amount]);
        return this.balance;
    }
    
    /**
     * Withdraw money from the account
     * @param {number} amount - Amount to withdraw
     * @return {number} New balance
     */
    withdraw(amount) {
        if (amount <= 0) {
            throw new Error("Withdrawal amount must be positive");
        }
        if (amount > this.balance) {
            throw new Error("Insufficient funds");
        }
        this.balance -= amount;
        this.transactions.push(["withdrawal", amount]);
        return this.balance;
    }
    
    /**
     * Get transaction history
     * @return {Array} List of transactions
     */
    getTransactionHistory() {
        return this.transactions;
    }
    
    /**
     * String representation of the account
     * @return {string} Account information
     */
    toString() {
        return `Account owner: ${this.owner}\nBalance: $${this.balance}`;
    }
}

// Create an account and perform operations
const account = new BankAccount("John Doe", 1000);
account.deposit(500);
account.withdraw(200);
console.log(account.toString());
console.log(`Transaction history: ${JSON.stringify(account.getTransactionHistory())}`);
```

### Algorithm Implementation (Quicksort)
```javascript
/**
 * Implement the quicksort algorithm to sort an array.
 * @param {Array} arr - The array to sort
 * @return {Array} The sorted array
 */
function quicksort(arr) {
    if (arr.length <= 1) {
        return arr;
    }
    
    const pivotIndex = Math.floor(arr.length / 2);
    const pivot = arr[pivotIndex];
    const left = [];
    const middle = [];
    const right = [];
    
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] < pivot) {
            left.push(arr[i]);
        } else if (arr[i] === pivot) {
            middle.push(arr[i]);
        } else {
            right.push(arr[i]);
        }
    }
    
    return [...quicksort(left), ...middle, ...quicksort(right)];
}

// Test the algorithm
const unsortedList = [3, 6, 8, 10, 1, 2, 1, 7];
const sortedList = quicksort(unsortedList);
console.log(`Unsorted: ${unsortedList}`);
console.log(`Sorted: ${sortedList}`);
```

### Code with Vulnerabilities
```javascript
const express = require('express');
const { exec } = require('child_process');
const sqlite3 = require('sqlite3').verbose();
const app = express();

app.use(express.urlencoded({ extended: true }));

// SQL Injection vulnerability
app.get('/users', (req, res) => {
    const query = req.query.name || '';
    const db = new sqlite3.Database('users.db');
    
    db.all(`SELECT * FROM users WHERE name LIKE '%${query}%'`, (err, rows) => {
        if (err) {
            return res.status(500).send(err.message);
        }
        res.json(rows);
    });
    
    db.close();
});

// Command Injection vulnerability
app.get('/ping', (req, res) => {
    const host = req.query.host || 'localhost';
    exec(`ping -c 4 ${host}`, (error, stdout, stderr) => {
        res.send(stdout);
    });
});

// XSS vulnerability
app.get('/search', (req, res) => {
    const query = req.query.q || '';
    res.send(`
        <h1>Search Results for: ${query}</h1>
        <p>No results found.</p>
    `);
});

// Insecure direct object reference
app.get('/documents/:id', (req, res) => {
    // No authorization check
    res.sendFile(`/documents/${req.params.id}`);
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

## Java

### Simple Function
```java
/**
 * Factorial calculation example
 */
public class Factorial {
    /**
     * Calculate the factorial of a number recursively.
     * @param n The input number
     * @return The factorial of n
     */
    public static long factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    public static void main(String[] args) {
        int number = 5;
        long result = factorial(number);
        System.out.println("Factorial of " + number + " is " + result);
    }
}
```

### Class Definition
```java
import java.util.ArrayList;
import java.util.List;

/**
 * A simple bank account class with deposit and withdrawal functionality.
 */
public class BankAccount {
    private String owner;
    private double balance;
    private List<Object[]> transactions;
    
    /**
     * Create a new bank account
     * @param owner The account owner's name
     * @param balance Initial balance
     */
    public BankAccount(String owner, double balance) {
        this.owner = owner;
        this.balance = balance;
        this.transactions = new ArrayList<>();
    }
    
    /**
     * Create a new bank account with zero balance
     * @param owner The account owner's name
     */
    public BankAccount(String owner) {
        this(owner, 0);
    }
    
    /**
     * Deposit money into the account
     * @param amount Amount to deposit
     * @return New balance
     * @throws IllegalArgumentException if amount is negative
     */
    public double deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Deposit amount must be positive");
        }
        this.balance += amount;
        this.transactions.add(new Object[]{"deposit", amount});
        return this.balance;
    }
    
    /**
     * Withdraw money from the account
     * @param amount Amount to withdraw
     * @return New balance
     * @throws IllegalArgumentException if amount is negative or exceeds balance
     */
    public double withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Withdrawal amount must be positive");
        }
        if (amount > this.balance) {
            throw new IllegalArgumentException("Insufficient funds");
        }
        this.balance -= amount;
        this.transactions.add(new Object[]{"withdrawal", amount});
        return this.balance;
    }
    
    /**
     * Get transaction history
     * @return List of transactions
     */
    public List<Object[]> getTransactionHistory() {
        return this.transactions;
    }
    
    /**
     * Get account owner
     * @return Account owner's name
     */
    public String getOwner() {
        return this.owner;
    }
    
    /**
     * Get current balance
     * @return Current balance
     */
    public double getBalance() {
        return this.balance;
    }
    
    @Override
    public String toString() {
        return "Account owner: " + this.owner + "\nBalance: $" + this.balance;
    }
    
    public static void main(String[] args) {
        BankAccount account = new BankAccount("John Doe", 1000);
        account.deposit(500);
        account.withdraw(200);
        System.out.println(account);
        System.out.println("Transaction history: " + account.getTransactionHistory());
    }
}
```

### Algorithm Implementation (Quicksort)
```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Implementation of the Quicksort algorithm
 */
public class Quicksort {
    /**
     * Sort an array using the quicksort algorithm
     * @param arr The array to sort
     * @return The sorted array
     */
    public static int[] quicksort(int[] arr) {
        if (arr.length <= 1) {
            return arr;
        }
        
        int pivotIndex = arr.length / 2;
        int pivot = arr[pivotIndex];
        
        List<Integer> left = new ArrayList<>();
        List<Integer> middle = new ArrayList<>();
        List<Integer> right = new ArrayList<>();
        
        for (int num : arr) {
            if (num < pivot) {
                left.add(num);
            } else if (num == pivot) {
                middle.add(num);
            } else {
                right.add(num);
            }
        }
        
        // Convert lists to arrays and combine
        int[] leftSorted = quicksort(listToArray(left));
        int[] rightSorted = quicksort(listToArray(right));
        
        // Combine the sorted arrays
        int[] result = new int[arr.length];
        int index = 0;
        
        for (int num : leftSorted) {
            result[index++] = num;
        }
        
        for (int num : middle) {
            result[index++] = num;
        }
        
        for (int num : rightSorted) {
            result[index++] = num;
        }
        
        return result;
    }
    
    /**
     * Convert a List<Integer> to an int[]
     */
    private static int[] listToArray(List<Integer> list) {
        int[] array = new int[list.size()];
        for (int i = 0; i < list.size(); i++) {
            array[i] = list.get(i);
        }
        return array;
    }
    
    public static void main(String[] args) {
        int[] unsortedList = {3, 6, 8, 10, 1, 2, 1, 7};
        int[] sortedList = quicksort(unsortedList);
        
        System.out.println("Unsorted: " + Arrays.toString(unsortedList));
        System.out.println("Sorted: " + Arrays.toString(sortedList));
    }
}
```

### Code with Vulnerabilities
```java
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/vulnerable")
public class VulnerableServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    
    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        String query = request.getParameter("q");
        String action = request.getParameter("action");
        
        response.setContentType("text/html");
        
        try {
            if ("search".equals(action)) {
                // SQL Injection vulnerability
                Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/mydb", "user", "password");
                Statement stmt = conn.createStatement();
                String sql = "SELECT * FROM users WHERE name LIKE '%" + query + "%'";
                ResultSet rs = stmt.executeQuery(sql);
                
                while (rs.next()) {
                    response.getWriter().println(rs.getString("name") + "<br>");
                }
                
                rs.close();
                stmt.close();
                conn.close();
            } else if ("ping".equals(action)) {
                // Command Injection vulnerability
                Process process = Runtime.getRuntime().exec("ping -c 4 " + query);
                java.util.Scanner s = new java.util.Scanner(process.getInputStream()).useDelimiter("\\A");
                String result = s.hasNext() ? s.next() : "";
                response.getWriter().println(result);
            } else {
                // XSS vulnerability
                response.getWriter().println("<h1>Search Results for: " + query + "</h1>");
                response.getWriter().println("<p>No results found.</p>");
            }
        } catch (SQLException e) {
            response.getWriter().println("Database error: " + e.getMessage());
        }
    }
}
```

## C++

### Simple Function
```cpp
#include <iostream>

/**
 * Calculate the factorial of a number recursively.
 * @param n The input number
 * @return The factorial of n
 */
long long factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int number = 5;
    long long result = factorial(number);
    std::cout << "Factorial of " << number << " is " << result << std::endl;
    return 0;
}
```

### Class Definition
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>

/**
 * A simple bank account class with deposit and withdrawal functionality.
 */
class BankAccount {
private:
    std::string owner;
    double balance;
    std::vector<std::pair<std::string, double>> transactions;

public:
    /**
     * Create a new bank account
     * @param owner The account owner's name
     * @param balance Initial balance
     */
    BankAccount(const std::string& owner, double balance = 0) 
        : owner(owner), balance(balance) {}
    
    /**
     * Deposit money into the account
     * @param amount Amount to deposit
     * @return New balance
     */
    double deposit(double amount) {
        if (amount <= 0) {
            throw std::invalid_argument("Deposit amount must be positive");
        }
        balance += amount;
        transactions.push_back(std::make_pair("deposit", amount));
        return balance;
    }
    
    /**
     * Withdraw money from the account
     * @param amount Amount to withdraw
     * @return New balance
     */
    double withdraw(double amount) {
        if (amount <= 0) {
            throw std::invalid_argument("Withdrawal amount must be positive");
        }
        if (amount > balance) {
            throw std::invalid_argument("Insufficient funds");
        }
        balance -= amount;
        transactions.push_back(std::make_pair("withdrawal", amount));
        return balance;
    }
    
    /**
     * Get transaction history
     * @return Reference to transactions vector
     */
    const std::vector<std::pair<std::string, double>>& getTransactionHistory() const {
        return transactions;
    }
    
    /**
     * Get account owner
     * @return Account owner's name
     */
    std::string getOwner() const {
        return owner;
    }
    
    /**
     * Get current balance
     * @return Current balance
     */
    double getBalance() const {
        return balance;
    }
    
    /**
     * String representation of the account
     */
    friend std::ostream& operator<<(std::ostream& os, const BankAccount& account) {
        os << "Account owner: " << account.owner << "\nBalance: $" << account.balance;
        return os;
    }
};

int main() {
    try {
        BankAccount account("John Doe", 1000);
        account.deposit(500);
        account.withdraw(200);
        
        std::cout << account << std::endl;
        
        std::cout << "Transaction history: " << std::endl;
        for (const auto& transaction : account.getTransactionHistory()) {
            std::cout << "- " << transaction.first << ": $" << transaction.second << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
    
    return 0;
}
```

### Algorithm Implementation (Quicksort)
```cpp
#include <iostream>
#include <vector>
#include <algorithm>

/**
 * Implement the quicksort algorithm to sort a vector.
 * @param arr The vector to sort
 * @return The sorted vector
 */
std::vector<int> quicksort(const std::vector<int>& arr) {
    if (arr.size() <= 1) {
        return arr;
    }
    
    int pivot = arr[arr.size() / 2];
    std::vector<int> left, middle, right;
    
    for (int num : arr) {
        if (num < pivot) {
            left.push_back(num);
        } else if (num == pivot) {
            middle.push_back(num);
        } else {
            right.push_back(num);
        }
    }
    
    std::vector<int> result;
    std::vector<int> sortedLeft = quicksort(left);
    std::vector<int> sortedRight = quicksort(right);
    
    result.insert(result.end(), sortedLeft.begin(), sortedLeft.end());
    result.insert(result.end(), middle.begin(), middle.end());
    result.insert(result.end(), sortedRight.begin(), sortedRight.end());
    
    return result;
}

// Helper function to print a vector
void printVector(const std::vector<int>& vec, const std::string& label) {
    std::cout << label << ": [";
    for (size_t i = 0; i < vec.size(); ++i) {
        std::cout << vec[i];
        if (i < vec.size() - 1) {
            std::cout << ", ";
        }
    }
    std::cout << "]" << std::endl;
}

int main() {
    std::vector<int> unsortedList = {3, 6, 8, 10, 1, 2, 1, 7};
    std::vector<int> sortedList = quicksort(unsortedList);
    
    printVector(unsortedList, "Unsorted");
    printVector(sortedList, "Sorted");
    
    return 0;
}
```

### Code with Vulnerabilities
```cpp
#include <iostream>
#include <string>
#include <cstdlib>
#include <fstream>
#include <vector>
#include <sqlite3.h>

// Simple web server simulation with vulnerabilities

class VulnerableServer {
private:
    sqlite3* db;
    
public:
    VulnerableServer() {
        // Initialize SQLite database
        sqlite3_open("users.db", &db);
    }
    
    ~VulnerableServer() {
        sqlite3_close(db);
    }
    
    // SQL Injection vulnerability
    std::vector<std::string> searchUsers(const std::string& query) {
        std::vector<std::string> results;
        
        // Vulnerable SQL query construction
        std::string sql = "SELECT * FROM users WHERE name LIKE '%" + query + "%'";
        
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) == SQLITE_OK) {
            while (sqlite3_step(stmt) == SQLITE_ROW) {
                const unsigned char* name = sqlite3_column_text(stmt, 1);
                results.push_back(std::string(reinterpret_cast<const char*>(name)));
            }
        }
        
        sqlite3_finalize(stmt);
        return results;
    }
    
    // Command Injection vulnerability
    std::string pingHost(const std::string& host) {
        // Vulnerable system command
        std::string cmd = "ping -c 4 " + host;
        
        // Execute the command and get output
        FILE* pipe = popen(cmd.c_str(), "r");
        if (!pipe) {
            return "Error executing command";
        }
        
        char buffer[128];
        std::string result = "";
        
        while (!feof(pipe)) {
            if (fgets(buffer, 128, pipe) != nullptr) {
                result += buffer;
            }
        }
        
        pclose(pipe);
        return result;
    }
    
    // Buffer Overflow vulnerability
    void processInput(const char* input) {
        char buffer[10];
        // Vulnerable: no bounds checking
        strcpy(buffer, input);
        std::cout << "Processed: " << buffer << std::endl;
    }
    
    // Insecure File Operations
    bool saveUserData(const std::string& userId, const std::string& data) {
        // Vulnerable: no path validation
        std::string filename = "user_data/" + userId + ".txt";
        std::ofstream file(filename);
        
        if (file.is_open()) {
            file << data;
            file.close();
            return true;
        }
        
        return false;
    }
};

int main() {
    VulnerableServer server;
    
    // Example usage of vulnerable functions
    std::vector<std::string> users = server.searchUsers("admin' OR '1'='1");
    std::cout << "Found users: " << users.size() << std::endl;
    
    std::string pingResult = server.pingHost("localhost; ls -la");
    std::cout << "Ping result: " << pingResult << std::endl;
    
    server.processInput("This string is too long and will cause a buffer overflow");
    
    server.saveUserData("../../../etc/passwd", "Hacked!");
    
    return 0;
}
```
