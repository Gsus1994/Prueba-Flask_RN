//Frontend/App/Screens/Pantallas/settings.tsx

import React, { useState } from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';
import { View, Text, TouchableOpacity, Alert, StyleSheet, ScrollView } from 'react-native';

import { TabScreenProps } from '../../Types/navigationTypes';
import AsyncStorage from '@react-native-async-storage/async-storage';

type Props = TabScreenProps<'Ajustes'>;

const SettingsScreen: React.FC<Props> = ({ navigation }) => {
    const [showTerms, setShowTerms] = useState(false);

    const handleToggleTerms = () => {
        setShowTerms(!showTerms);
    };

    const handleContact = () => {
        Alert.alert('Contacto', 'Contacto para denuncias: contacto@empresa.com');
    };

    const handleLogout = async () => {
        try {
            await AsyncStorage.removeItem('access_token');

            navigation.reset({
                index: 0,
                routes: [{ name: 'Login' as never }],
            });

            Alert.alert('Sesión cerrada', 'Has cerrado sesión exitosamente.');
        } catch (error) {
            console.error('Error al cerrar sesión:', error);
            Alert.alert('Error', 'No se pudo cerrar la sesión. Por favor, intenta nuevamente.');
        }
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <ScrollView contentContainerStyle={styles.scrollContainer}>
                <View style={styles.container}>
                    <Text style={styles.title}>Ajustes</Text>

                    <TouchableOpacity
                        onPress={handleToggleTerms}
                        style={styles.toggleButton}
                    >
                        <Text style={styles.toggleButtonText}>Términos y Condiciones</Text>
                    </TouchableOpacity>
                    {showTerms && (
                        <View style={styles.termsContainer}>
                            <Text style={styles.termsText}>
                                Estos son los términos y condiciones de uso de la aplicación. Al
                                utilizarla, aceptas cumplir con las normas y regulaciones de la
                                plataforma...
                                {/* Aquí se debe añadir el texto completo de los términos */}
                            </Text>
                        </View>
                    )}

                    <TouchableOpacity
                        style={styles.contactButton}
                        onPress={handleContact}
                    >
                        <Text style={styles.buttonText}>Contacto para Denuncias</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={styles.logoutButton}
                        onPress={handleLogout}
                    >
                        <Text style={styles.buttonText}>Cerrar Sesión</Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
};

export default SettingsScreen;

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
        backgroundColor: '#f0f0f0',
    },
    scrollContainer: {
        flexGrow: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    container: { width: '90%' },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        textAlign: 'center',
        marginBottom: 50,
    },
    toggleButton: {
        backgroundColor: '#4CAF50',
        padding: 15,
        borderRadius: 10,
        marginBottom: 20,
        width: '100%',
        alignItems: 'center',
    },
    toggleButtonText: { color: '#fff', fontSize: 16 },
    termsContainer: {
        backgroundColor: '#ffffff',
        padding: 15,
        borderRadius: 10,
        marginBottom: 20,
        width: '100%',
    },
    termsText: { fontSize: 14, color: '#333' },
    contactButton: {
        backgroundColor: '#FF9800',
        padding: 15,
        borderRadius: 10,
        marginBottom: 20,
        width: '100%',
        alignItems: 'center',
    },
    logoutButton: {
        backgroundColor: '#f44336',
        padding: 15,
        borderRadius: 10,
        width: '100%',
        alignItems: 'center',
    },
    buttonText: { color: '#fff', fontSize: 16 },
});