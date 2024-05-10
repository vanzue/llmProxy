require('dotenv').config();
const express = require('express');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

const azureEndpointDalle = process.env.AZURE_ENDPOINT_DALLE;
const deploymentModelDalle = "Dalle3"
const apiVersionDalle = "2024-02-01"

const azureEndpointGpt35 = process.env.AZURE_ENDPOINT_GPT35;
const deploymentModelGpt35 = "35turbojapan"
const apiVersionGpt35 = "2024-02-15-preview"

const dalleEndpoint = `${azureEndpointDalle}/openai/deployments/${deploymentModelDalle}/images/generations?api-version=${apiVersionDalle}`;
const gpt35Endpoint = `${azureEndpointGpt35}/openai/deployments/${deploymentModelGpt35}/chat/completions?api-version=${apiVersionGpt35}`;

const azureApiKeyDalle = process.env.AZURE_API_KEY_DALLE;
const azureApiKeyGpt35 = process.env.AZURE_API_KEY_GPT35;


app.get('/ping', async (req, res) => {
    res.json({ message: 'pong' });
});

app.post('/dalle', async (req, res) => {
    try {
        const response = await axios.post(dalleEndpoint, req.body, {
            headers: {
                'api-key': azureApiKeyDalle,
                'Content-Type': 'application/json'
            }
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ message: 'Error communicating with DALL-E service', details: error.message });
    }
});

app.post('/gpt35', async (req, res) => {
    try {
        const response = await axios.post(gpt35Endpoint, req.body, {
            headers: {
                'api-key': azureApiKeyGpt35,
                'Content-Type': 'application/json'
            }
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ message: 'Error communicating with GPT35 service', details: error.message });
    }
});

app.post('/generate/scenes', async (req, res) => {
    const deploymentModel = "kaigpt4"
    const apiVersion = "2024-02-15-preview"
    const azureEndpoint = process.env.AZURE_ENDPOINT_GPT4;
    const azureApiKey = process.env.AZURE_API_KEY_GPT4;

    const endpoint = `${azureEndpoint}/openai/deployments/${deploymentModel}/chat/completions?api-version=${apiVersion}`;
    
    let chatResult = null;
    // Use to generate scenes for comic.
    try {
        chatResult = await axios.post(endpoint, req.body, {
            headers: {
                'api-key': azureApiKey,
                'Content-Type': 'application/json'
            }
        });

    } catch (error) {
        console.log(error.message);
        res.status(500).json({ message: 'Error communicating with GPT4 service', details: error.message });
    }

    let stories = chatResult.data.choices[0].message.content;

    const cleanJsonString = stories.replace(/```json\n|\n```/g, "").trim();

    // Parse the cleaned string into an array of strings
    const scenes = JSON.parse(cleanJsonString);

    // Output the list of descriptions
    console.log("scenes:", scenes);
    
    res.json(scenes);
});


app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
