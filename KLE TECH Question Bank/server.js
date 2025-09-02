const express = require('express');
const { MongoClient } = require('mongodb');

const app = express();
const port = 3000;

// MongoDB connection URI
const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

app.use(express.static('public')); // Assuming your HTML file is in the "public" directory

app.use(express.urlencoded({ extended: true }));

app.post('/signup', async (req, res) => {
    try {
        await client.connect();
        const database = client.db('your-database-name');
        const collection = database.collection('users');

        // Assuming form fields have "name", "email", and "password"
        const user = {
            name: req.body.name,
            email: req.body.email,
            password: req.body.password,
        };

        const result = await collection.insertOne(user);

        res.status(200).json({ message: 'User registered successfully', insertedId: result.insertedId });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
