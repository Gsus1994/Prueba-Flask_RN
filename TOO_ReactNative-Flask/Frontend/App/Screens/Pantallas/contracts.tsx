//Frontend/App/Screens/Pantallas/contracts.tsx

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const ContractsScreen = () => {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Pantalla de Acuerdos pasados y actuales</Text>
        </View>
    );
};

export default ContractsScreen;

const styles = StyleSheet.create({
    container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    title: { fontSize: 24 },
});