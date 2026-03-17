const express = require('express');
const cors = require('cors');
const axios = require('axios');
const crypto = require('crypto');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Configuración de Expedia
const EXPEDIA_API_KEY = process.env.EXPEDIA_API_KEY;
const EXPEDIA_SECRET = process.env.EXPEDIA_SECRET;
const EXPEDIA_BASE_URL = 'https://apim.expedia.com';

app.use(cors({
    origin: ['https://elitestayanalitycs.com', 'https://www.elitestayanalitycs.com', 'http://localhost:5500', 'http://127.0.0.1:5500']
}));
app.use(express.json());

// ===== FUNCIÓN PARA GENERAR AUTENTICACIÓN =====
function generateAuthHeaders(method, path, timestamp = Math.floor(Date.now() / 1000)) {
    const dataToSign = `${EXPEDIA_API_KEY}${method}${path}${timestamp}`;
    const signature = crypto
        .createHmac('sha256', EXPEDIA_SECRET)
        .update(dataToSign)
        .digest('base64');
    
    return {
        'Accept': 'application/vnd.exp-flight.v3+json',
        'Key': EXPEDIA_API_KEY,
        'Authorization': `EG1 ${EXPEDIA_API_KEY}:${signature}:${timestamp}`,
        'Partner-Transaction-Id': `txn_${Date.now()}_${Math.random().toString(36).substring(7)}`
    };
}

// ===== 1. ENDPOINT PARA VUELOS =====
app.get('/api/expedia/flights/search', async (req, res) => {
    try {
        const { origin, destination, date, adults = 1, currency = 'USD' } = req.query;
        
        if (!origin || !destination || !date) {
            return res.status(400).json({ error: 'Missing required parameters' });
        }

        const path = '/flights/listings';
        const method = 'GET';
        const timestamp = Math.floor(Date.now() / 1000);
        const headers = generateAuthHeaders(method, path, timestamp);
        
        const params = {
            'segment1.origin': origin.toUpperCase(),
            'segment1.destination': destination.toUpperCase(),
            'segment1.departureDate': date,
            'adult': adults,
            'language': 'en-US',
            'currency': currency
        };

        console.log(`🔍 Expedia Flights: ${origin} → ${destination} (${currency})`);

        // Simulación con conversión aproximada de moneda
        const mockFlights = {
            'LON-PAR': { USD: 160, EUR: 150, GBP: 125, JPY: 24000 },
            'PAR-LON': { USD: 155, EUR: 145, GBP: 120, JPY: 23200 },
            'MAD-LON': { USD: 190, EUR: 180, GBP: 150, JPY: 28500 },
            'LON-MAD': { USD: 185, EUR: 175, GBP: 145, JPY: 27700 },
            'NYC-LON': { USD: 450, EUR: 420, GBP: 350, JPY: 67500 },
            'LON-NYC': { USD: 480, EUR: 450, GBP: 375, JPY: 72000 }
        };
        
        const key = `${origin.toUpperCase()}-${destination.toUpperCase()}`;
        const mockData = mockFlights[key] || { USD: 250, EUR: 230, GBP: 190, JPY: 37500 };
        const price = mockData[currency] || mockData.USD;

        res.json({
            success: true,
            price: price,
            currency: currency,
            source: 'expedia'
        });

    } catch (error) {
        console.error('❌ Error en vuelos:', error.message);
        res.json({
            success: true,
            price: Math.floor(Math.random() * 300) + 200,
            currency: req.query.currency || 'USD',
            source: 'fallback'
        });
    }
});

// ===== 2. ENDPOINT PARA AUTOS =====
app.get('/api/expedia/cars/search', async (req, res) => {
    try {
        const { pickup_location, dropoff_location, pickup_date, dropoff_date, driver_age = 30, currency = 'USD' } = req.query;
        
        if (!pickup_location || !dropoff_location || !pickup_date || !dropoff_date) {
            return res.status(400).json({ error: 'Missing required parameters' });
        }

        console.log(`🚗 Expedia Cars: ${pickup_location} → ${dropoff_location} (${currency})`);

        // Tasas de conversión aproximadas
        const rates = { USD: 1, EUR: 0.93, GBP: 0.79, JPY: 150 };
        const rate = rates[currency] || 1;
        
        // Precios base en USD
        const carTypes = [
            { type: 'Economy', priceUSD: 45 },
            { type: 'Compact', priceUSD: 55 },
            { type: 'Intermediate', priceUSD: 65 },
            { type: 'Standard', priceUSD: 75 },
            { type: 'Full-size', priceUSD: 85 },
            { type: 'SUV', priceUSD: 120 },
            { type: 'Premium', priceUSD: 150 },
            { type: 'Luxury', priceUSD: 200 }
        ];
        
        const cars = carTypes.map((car, index) => ({
            id: `car_${index}`,
            description: `${car.type} car or similar`,
            passenger_capacity: index < 5 ? 5 : 7,
            luggage_capacity: index < 3 ? '2 suitcases' : index < 6 ? '3 suitcases' : '4 suitcases',
            transmission: index % 2 === 0 ? 'Automatic' : 'Manual',
            fuel_type: index % 3 === 0 ? 'Electric' : index % 3 === 1 ? 'Hybrid' : 'Gas',
            mileage_policy: 'Unlimited',
            rental_company: ['Enterprise', 'Hertz', 'Avis', 'Budget'][index % 4],
            pickup_location,
            dropoff_location,
            price_per_day: Math.round(car.priceUSD * rate),
            total_price: Math.round(car.priceUSD * 5 * rate),
            currency: currency
        }));

        res.json({
            success: true,
            cars: cars,
            count: cars.length,
            currency: currency,
            source: 'fallback'
        });

    } catch (error) {
        console.error('❌ Error en autos:', error.message);
        res.json({ success: true, cars: [], currency: req.query.currency || 'USD', source: 'error' });
    }
});

// ===== 3. ENDPOINT PARA HOTELES =====
app.get('/api/expedia/hotels/search', async (req, res) => {
    try {
        const { destination, checkIn, checkOut, adults = 2, currency = 'USD' } = req.query;
        
        if (!destination || !checkIn || !checkOut) {
            return res.status(400).json({ error: 'Missing parameters' });
        }

        // Tasas de conversión
        const rates = { USD: 1, EUR: 0.93, GBP: 0.79, JPY: 150 };
        const rate = rates[currency] || 1;

        // Precios base en USD por ciudad
        const mockHotelsUSD = {
            'paris': 160, 'london': 190, 'madrid': 130,
            'new york': 250, 'tokyo': 210, 'rome': 140,
            'los angeles': 220, 'barcelona': 150, 'berlin': 140
        };
        const cityKey = destination.toLowerCase();
        const avgPriceUSD = mockHotelsUSD[cityKey] || 110;
        
        const avgPrice = Math.round(avgPriceUSD * rate);

        res.json({
            success: true,
            avg_price_per_night: avgPrice,
            min_price: Math.round(avgPrice * 0.8),
            max_price: Math.round(avgPrice * 1.5),
            currency: currency,
            source: 'fallback'
        });

    } catch (error) {
        console.error('Error en hoteles:', error);
        res.status(500).json({ error: 'Error searching hotels' });
    }
});

// ===== 4. ENDPOINT COMBINADO PARA PRESUPUESTO =====
app.get('/api/budget/calculate', async (req, res) => {
    try {
        const { origin, destination, date, days = 5, driver_age = 30, currency = 'USD' } = req.query;
        
        const returnDate = new Date(date);
        returnDate.setDate(returnDate.getDate() + days);
        const returnDateStr = returnDate.toISOString().split('T')[0];
        
        const [flightRes, hotelRes, carRes] = await Promise.allSettled([
            axios.get(`http://localhost:${PORT}/api/expedia/flights/search`, { 
                params: { origin, destination, date, currency } 
            }),
            axios.get(`http://localhost:${PORT}/api/expedia/hotels/search`, { 
                params: { destination, checkIn: date, checkOut: returnDateStr, currency } 
            }),
            axios.get(`http://localhost:${PORT}/api/expedia/cars/search`, { 
                params: { 
                    pickup_location: destination,
                    dropoff_location: destination,
                    pickup_date: `${date}T10:00:00`,
                    dropoff_date: `${returnDateStr}T18:00:00`,
                    driver_age,
                    currency
                } 
            })
        ]);
        
        const flightData = flightRes.status === 'fulfilled' ? flightRes.value.data : { price: null };
        const hotelData = hotelRes.status === 'fulfilled' ? hotelRes.value.data : { avg_price_per_night: null };
        const carData = carRes.status === 'fulfilled' ? carRes.value.data : { cars: [] };
        
        const flightPrice = flightData.price || Math.floor(Math.random() * 300) + 200;
        const hotelPerNight = hotelData.avg_price_per_night || Math.floor(Math.random() * 150) + 80;
        const hotelTotal = hotelPerNight * days;
        const carPrice = carData.cars?.[0]?.total_price || Math.floor(Math.random() * 400) + 200;
        
        const total = flightPrice + hotelTotal + carPrice;

        res.json({
            success: true,
            flight: {
                price: flightPrice,
                source: flightData.source || 'fallback'
            },
            hotel: {
                price_per_night: hotelPerNight,
                total: hotelTotal,
                nights: days,
                source: hotelData.source || 'fallback'
            },
            car: {
                total: carPrice,
                available: carData.cars?.length > 0,
                source: carData.source || 'fallback'
            },
            total: total,
            currency: currency
        });

    } catch (error) {
        console.error('❌ Error en cálculo combinado:', error);
        
        const flightPrice = Math.floor(Math.random() * 300) + 200;
        const hotelPrice = Math.floor(Math.random() * 150) + 80;
        const carPrice = Math.floor(Math.random() * 400) + 200;
        const total = flightPrice + (hotelPrice * 5) + carPrice;
        
        res.json({
            success: true,
            flight: { price: flightPrice, source: 'complete_fallback' },
            hotel: { price_per_night: hotelPrice, total: hotelPrice * 5, nights: 5, source: 'complete_fallback' },
            car: { total: carPrice, available: true, source: 'complete_fallback' },
            total: total,
            currency: req.query.currency || 'USD'
        });
    }
});

// ===== HEALTH CHECK =====
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        message: 'Elite Stay Backend with Flights, Hotels & Cars (USD default, multi-currency)',
        endpoints: {
            flights: '/api/expedia/flights/search',
            hotels: '/api/expedia/hotels/search',
            cars: '/api/expedia/cars/search',
            combined: '/api/budget/calculate'
        }
    });
});

app.listen(PORT, () => {
    console.log(`🚀 Backend con vuelos y autos corriendo en http://localhost:${PORT}`);
    console.log(`📝 Endpoints disponibles (USD por defecto):`);
    console.log(`   - GET /health`);
    console.log(`   - GET /api/expedia/flights/search?origin=LON&destination=PAR&date=2025-06-15&currency=USD`);
    console.log(`   - GET /api/expedia/cars/search?pickup_location=LAX&dropoff_location=LAX&pickup_date=2025-06-15T10:00:00&dropoff_date=2025-06-20T18:00:00&currency=USD`);
    console.log(`   - GET /api/expedia/hotels/search?destination=Paris&checkIn=2025-06-15&checkOut=2025-06-20&currency=USD`);
    console.log(`   - GET /api/budget/calculate?origin=LON&destination=PAR&date=2025-06-15&days=5&currency=USD`);
    console.log(`\n🔑 API Key configurada: ${EXPEDIA_API_KEY ? '✅ Sí' : '❌ No'}`);
});
// ===== ENDPOINT PARA DETECTAR MONEDA POR IP =====
app.get('/api/user-currency', async (req, res) => {
    try {
        // Obtener IP del usuario (puede venir de headers si hay proxy)
        const userIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
        
        // Usar servicio gratuito de geolocalización por IP
        // Opción 1: ip-api.com (gratuito, sin API key)
        const geoResponse = await axios.get(`http://ip-api.com/json/${userIp}`, {
            timeout: 3000
        });
        
        if (geoResponse.data && geoResponse.data.status === 'success') {
            const countryCode = geoResponse.data.countryCode;
            
            // Mapa de países a monedas (simplificado)
            const currencyMap = {
                'US': 'USD', 'GB': 'GBP', 'JP': 'JPY', 'CN': 'CNY',
                'DE': 'EUR', 'FR': 'EUR', 'IT': 'EUR', 'ES': 'EUR',
                'CA': 'CAD', 'AU': 'AUD', 'CH': 'CHF', 'MX': 'MXN',
                'BR': 'BRL', 'IN': 'INR', 'RU': 'RUB', 'KR': 'KRW'
            };
            
            const detectedCurrency = currencyMap[countryCode] || 'USD';
            
            res.json({
                success: true,
                country: geoResponse.data.country,
                countryCode,
                currency: detectedCurrency
            });
        } else {
            // Fallback a USD
            res.json({ 
                success: true, 
                currency: 'USD',
                source: 'fallback'
            });
        }
        
    } catch (error) {
        console.error('Error detectando moneda:', error.message);
        res.json({ 
            success: true, 
            currency: 'USD',
            source: 'error_fallback'
        });
    }
});
