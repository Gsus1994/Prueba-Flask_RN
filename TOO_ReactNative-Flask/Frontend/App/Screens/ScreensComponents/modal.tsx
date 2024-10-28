// Frontend/App/Screens/ScreensComponents/modal.tsx

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal as RNModal } from 'react-native';

interface ModalProps {
    visible: boolean;
    onClose: () => void;
    onTakePhoto: () => void;
    onPickFromGallery: () => void;
}

const Modal: React.FC<ModalProps> = ({ visible, onClose, onTakePhoto, onPickFromGallery }) => {
    return (
        <RNModal
            animationType="slide"
            transparent={true}
            visible={visible}
            onRequestClose={onClose}
        >
            <View style={styles.modalOverlay}>
                <View style={styles.modalView}>
                    <TouchableOpacity
                        style={styles.modalButton}
                        onPress={onTakePhoto}
                    >
                        <Text style={styles.modalButtonText}>Tomar foto</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={styles.modalButton}
                        onPress={onPickFromGallery}
                    >
                        <Text style={styles.modalButtonText}>Elegir de la galería</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={[styles.modalButton, styles.cancelButton]}
                        onPress={onClose}
                    >
                        <Text style={styles.modalButtonText}>Cancelar</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </RNModal>
    );
};

export default Modal;

const styles = StyleSheet.create({
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    modalView: {
        backgroundColor: '#fff',
        borderRadius: 10,
        paddingVertical: 20,
        paddingHorizontal: 30,
        width: '80%',
        alignItems: 'center',
    },
    modalButtonText: {
        fontSize: 16,
        color: '#007AFF',
    },
    modalButton: {
        paddingVertical: 15,
        width: '100%',
        alignItems: 'center',
        borderBottomWidth: 2,
        borderColor: '#zzz',
    },
    cancelButton: {
        paddingVertical: 15,
        width: '100%',
        alignItems: 'center',
        borderBottomWidth: 2,
        borderColor: '#zzz',
    },
});