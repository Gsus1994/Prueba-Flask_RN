// Frontend/App/Screens/Auth/login.tsx

import React, { useState } from 'react';
import {
    View,
    TextInput,
    Button,
    Text,
    Image,
    TouchableOpacity,
    Alert,
    StyleSheet,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import Loader from '../ScreensComponents/loader';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import { loginUser } from '../../Services/authServices';
import { StackScreenProps } from '@react-navigation/stack';
import { SafeAreaView } from 'react-native-safe-area-context';

import { LoginResponse, LoginData } from '../../Types/formTypes';
import { RootStackParamList } from '../../Types/navigationTypes';

type Props = StackScreenProps<RootStackParamList, 'Login'>;

const LoginScreen: React.FC<Props> = ({ navigation }) => {
    const [user, setUser] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);

    const hacerLogin = async () => {
        const userData: LoginData = {
            username: user,
            password: password,
        };

        if (!user || !password) {
            Alert.alert('Error', 'Por favor, completa todos los campos.');
            return;
        }

        setLoading(true);

        try {
            const response: LoginResponse = await loginUser(userData);
            const token = response.access_token;
            await AsyncStorage.setItem('access_token', token);
            navigation.replace('HomeTabs');
        } catch (error: any) {
            console.error('Error en el login:', error);

            let errorMsg = 'Ocurrió un error inesperado.';

            if (error.message) {
                errorMsg = error.message;
            } else {
                errorMsg = 'No se pudo conectar con el servidor. Verifica tu conexión.';
            }

            Alert.alert('Error', errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const goToSignup = () => {
        navigation.navigate('Signup');
    };

    const goToRecovery = () => {
        navigation.navigate('Recovery');
    };

    return (
        <LinearGradient
            colors={['#ffffff', '#909090']}
            style={styles.safeArea}
            start={{ x: 0.5, y: 1 }}
            end={{ x: 1, y: 0.75 }}
        >
            <SafeAreaView style={styles.safeArea}>
                <View style={styles.container}>
                    <Text style={styles.title}>Inicio de Sesión</Text>
                    <Image
                        source={require('../../Assets/Images/240509_Too_Logo_Gris_Oscuro.png')}
                        style={styles.image}
                        resizeMode="contain"
                    />
                    <View style={styles.inputContainer}>
                        <Icon name="user" size={20} color="#000" style={styles.icon} />
                        <TextInput
                            style={styles.input}
                            placeholder="Correo electrónico"
                            value={user}
                            onChangeText={setUser}
                            keyboardType="email-address"
                            autoCapitalize="none"
                        />
                    </View>
                    <View style={styles.inputContainer}>
                        <Icon name="lock" size={20} color="#000" style={styles.icon} />
                        <TextInput
                            style={styles.input}
                            placeholder="Contraseña"
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry={!showPassword}
                        />
                        <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                            <Icon
                                name={showPassword ? 'eye-slash' : 'eye'}
                                size={20}
                                color="#000"
                                style={styles.icon}
                            />
                        </TouchableOpacity>
                    </View>
                    <View style={styles.buttonContainer}>
                        <Button title="Login" onPress={hacerLogin} />
                    </View>
                    <TouchableOpacity onPress={goToSignup}>
                        <Text style={styles.signupText}>¿No formas parte? Únete</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={goToRecovery}>
                        <Text style={styles.recoveryText}>¿Olvidaste la contraseña? Recupérala</Text>
                    </TouchableOpacity>
                </View>
                {/* Agrega el Loader */}
                <Loader visible={loading} message="Iniciando sesión..." />
            </SafeAreaView>
        </LinearGradient>
    );
};

export default LoginScreen;

const styles = StyleSheet.create({
    safeArea: { flex: 1 },
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 20,
        borderBottomWidth: 1,
        borderColor: '#000',
        width: 300,
    },
    input: {
        height: 40,
        flex: 1,
        paddingHorizontal: 10,
    },
    icon: { paddingHorizontal: 10 },
    title: {
        fontSize: 24,
        marginBottom: 20,
        textAlign: 'center',
        color: '#333',
    },
    image: {
        width: 200,
        height: 150,
        marginBottom: 20,
    },
    buttonContainer: {
        width: 210,
        marginTop: 20,
    },
    signupText: {
        marginTop: 65,
        color: '#0000EE',
        textDecorationLine: 'underline',
    },
    recoveryText: {
        marginTop: 30,
        color: '#0000EE',
        textDecorationLine: 'underline',
    },
});