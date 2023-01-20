from micropython import const
import pyb
import struct
import bluetooth

# Les constantes pour les différents types d'événements BLE
_IRQ_CENTRAL_CONNECT = const(1) # Connexion d'un périphérique central
_IRQ_CENTRAL_DISCONNECT = const(2) # Déconnexion d'un périphérique central
_IRQ_GATTS_WRITE = const(3) # Ecriture de données par un périphérique central
_IRQ_GATTS_READ_REQUEST = const(4) # Demande de lecture de données par un périphérique central
_IRQ_SCAN_RESULT = const(5) # Résultat d'une recherche de périphériques
_IRQ_SCAN_DONE = const(6) # Fin d'une recherche de périphériques
_IRQ_PERIPHERAL_CONNECT = const(7) # Connexion d'un périphérique
_IRQ_PERIPHERAL_DISCONNECT = const(8) # Déconnexion d'un périphérique
_IRQ_GATTC_SERVICE_RESULT = const(9) # Résultat d'une recherche de service par un périphérique central
_IRQ_GATTC_SERVICE_DONE = const(10) # Fin d'une recherche de service par un périphérique central
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11) # Résultat d'une recherche de caractéristique par un périphérique central
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12) # Fin d'une recherche de caractéristique par un périphérique central
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13) # Résultat d'une recherche de descripteur par un périphérique central
_IRQ_GATTC_DESCRIPTOR_DONE = const(14) # Fin d'une recherche de descripteur par un périphérique central
_IRQ_GATTC_READ_RESULT = const(15) # Résultat de la lecture de données par un périphérique central
_IRQ_GATTC_READ_DONE = const(16) # Fin de la lecture de données par un périphérique central
_IRQ_GATTC_WRITE_DONE = const(17) # Fin de l'écriture de données par un périphérique central
_IRQ_GATTC_NOTIFY = const(18) # Notification envoyée par un périphérique
_IRQ_GATTC_INDICATE = const(19) # Indication envoyée par un périphérique
_IRQ_GATTS_INDICATE_DONE = const(20) # Fin d'une indication envoyée par un périphérique
_IRQ_MTU_EXCHANGED = const(21) # Échange de la taille de la MTU (Maximum Transmission Unit)
_IRQ_L2CAP_ACCEPT = const(22) # Acceptation d'une connexion L2CAP
_IRQ_L2CAP_CONNECT = const(23) # Connexion L2CAP
_IRQ_L2CAP_DISCONNECT = const(24) # Déconnexion L2CAP
_IRQ_L2CAP_RECV = const(25) # Réception de données L2CAP
_IRQ_L2CAP_SEND_READY = const(26) # Prêt à envoyer des données L2CAP
_IRQ_CONNECTION_UPDATE = const(27) # Mise à jour de la connexion
_IRQ_ENCRYPTION_UPDATE = const(28) # Mise à jour du chiffrement
_IRQ_GET_SECRET = const(29) # Récupération d'un secret
_IRQ_SET_SECRET = const(30) # Définition d'un secret

# Les paquets publicitaires sont des paquets répétés de la forme suivante :
#   1 octet de longueur de données (N + 1)
#   1 octet de type (voir les constantes ci-dessous)
#   N octets de données spécifiques au type
_ADV_TYPE_FLAGS = const(0x01) # Type de données : drapeaux
_ADV_TYPE_NAME = const(0x09) # Type de données : nom
_ADV_TYPE_UUID16_COMPLETE = const(0x3) # Type de données : UUID 16 bits complet
_ADV_TYPE_UUID32_COMPLETE = const(0x5) # Type de données : UUID 32 bits complet
_ADV_TYPE_UUID128_COMPLETE = const(0x7) # Type de données : UUID 128 bits complet
_ADV_TYPE_UUID16_MORE = const(0x2) # Type de données : UUID 16 bits supplémentaire
_ADV_TYPE_UUID32_MORE = const(0x4) # Type de données : UUID 32 bits supplémentaire
_ADV_TYPE_UUID128_MORE = const(0x6) # Type de données : UUID 128 bits supplémentaire
_ADV_TYPE_APPEARANCE = const(0x19) # Type de données : apparence

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128) # Apparence générique d'un ordinateur

# Génère un paquet à passer à gap_advertise(adv_data=...).
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack('BB', len(value) + 1, adv_type) + value

    # Ajout des drapeaux de découverte limitée et/ou BR/EDR
    _append(_ADV_TYPE_FLAGS, struct.pack('B', (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04)))

    # Ajout du nom du périphérique s'il est spécifié
    if name:
        _append(_ADV_TYPE_NAME, name)

    # Ajout des UUID des services offerts s'ils sont spécifiés
    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)
            else:
                raise ValueError("Invalid UUID: {}".format(uuid))

    # Ajout de l'apparence du périphérique s'il est spécifié
    if appearance:
        _append(_ADV_TYPE_APPEARANCE, struct.pack('<h', appearance))

    return bytes(payload)


def decode_field(payload, adv_type):
    i = 0
    result = []
    while i + 1 < len(payload):
        if payload[i + 1] == adv_type:
            result.append(payload[i + 2:i + payload[i] + 1])
        i += 1 + payload[i]
    return result


def decode_name(payload):
    n = decode_field(payload, _ADV_TYPE_NAME)
    return str(n[0], 'utf-8') if n else ''


def decode_services(payload):
    services = []
    for u in decode_field(payload, _ADV_TYPE_UUID16_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack('<h', u)[0]))
    for u in decode_field(payload, _ADV_TYPE_UUID32_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack('<d', u)[0]))
    for u in decode_field(payload, _ADV_TYPE_UUID128_COMPLETE):
        services.append(bluetooth.UUID(u))
    return services

class Bleuart:
    def __init__(self, name, UUID_UART, UUID_TX, UUID_RX, rxbuf=100):
        _UART_UUID = bluetooth.UUID(UUID_UART,)
        _UART_TX = (bluetooth.UUID(UUID_TX), bluetooth.FLAG_NOTIFY,)
        _UART_RX = (bluetooth.UUID(UUID_RX), bluetooth.FLAG_WRITE,)
        _UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX,),)

        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle,),) = self._ble.gatts_register_services((_UART_SERVICE,))
        # Augmente la taille du buffer rx et active le mode append
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._connections = set()
        self._rx_buffer = bytearray()
        self._handler = None
        # Optionellement on peut ajouter services=[_UART_UUID], mais ca risque juste de rendre le payload trop gros
        self._payload = advertising_payload(name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()

    def irq(self, handler):
        self._handler = handler

    def _irq(self, event, data):
        # Piste les connections pour pouvoir envoyer des notifications
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
            pyb.LED(2).on()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _, = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
                pyb.LED(2).off()
            # Recommence a faire des annonces pour permettre une nouvelle connection
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle, = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(self._rx_handle)
                if self._handler:
                    self._handler()

    def any(self):
        return len(self._rx_buffer)

    def read(self, sz=None):
        if not sz:
            sz = len(self._rx_buffer)
        result = self._rx_buffer[0:sz]
        self._rx_buffer = self._rx_buffer[sz:]
        return result

    def write(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)

    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)