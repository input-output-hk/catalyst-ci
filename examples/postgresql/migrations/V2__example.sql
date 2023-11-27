CREATE TABLE address
(
  name VARCHAR PRIMARY KEY,
  address TEXT NOT NULL,

  FOREIGN KEY(name) REFERENCES users(name)
);
