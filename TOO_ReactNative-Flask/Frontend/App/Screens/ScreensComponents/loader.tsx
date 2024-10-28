// Frontend/App/Screens/ScreensComponents/loader.tsx

import React from 'react';
import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';

interface LoaderProps {
    visible: boolean;
    message?: string;
}

const Loader: React.FC<LoaderProps> = ({ visible, message }) => {
    if (!visible) return null;

    return (
        <View style={styles.overlay}>
            <View style={styles.loaderContainer}>
                <ActivityIndicator size="large" color="#0000ff" />
                {message && <Text style={styles.message}>{message}</Text>}
            </View>
        </View>
    );
};

export default Loader;

const styles = StyleSheet.create({
    overlay: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.3)',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
    },
    loaderContainer: {
        padding: 20,
        backgroundColor: '#fff',
        borderRadius: 10,
        alignItems: 'center',
    },
    message: {
        marginTop: 10,
        fontSize: 16,
        color: '#000',
    },
});