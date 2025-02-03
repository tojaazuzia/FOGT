import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib
matplotlib.use('TkAgg')

# Funkcja obliczająca intensywność interferencji na ekranie
def calculate_intensity(wavelength, amplitude, d, L, screen_width, resolution, slit_width):
    x = np.linspace(-screen_width / 2, screen_width / 2, resolution)
    k = 2 * np.pi / wavelength  # Liczba falowa

    # Obliczanie faz dla dwóch szczelin
    path_diff1 = np.sqrt(L**2 + (x - d/2)**2)
    path_diff2 = np.sqrt(L**2 + (x + d/2)**2)

    # Amplitudy fal z obu szczelin
    wave1 = amplitude * np.cos(k * path_diff1)
    wave2 = amplitude * np.cos(k * path_diff2)

    # Intensywność jest proporcjonalna do kwadratu sumy amplitud
    intensity = (wave1 + wave2)**2
    return x, intensity

# Funkcja generująca pole falowe zgodnie z zasadą Hugensa
def generate_huygens_wave(x, y, sources, wavelength, amplitude, screen_distance, slit_width):
    k = 2 * np.pi / wavelength
    field = np.zeros_like(x, dtype=np.complex128)

    for source_x, source_y in sources:
        r = np.sqrt((x - source_x)**2 + (y - source_y)**2 + screen_distance**2)  # Uwzględnienie odległości ekranu
        field += amplitude * np.exp(-1j * k * r) / r

    return np.abs(field)  # Zwracamy moduł pola falowego

# Parametry początkowe
wavelength = 500e-9  # Długość fali w metrach (500 nm)
amplitude = 1        # Amplituda
slit_distance = 1e-3 # Odległość między szczelinami (1 mm)
slit_width = 1e-4    # Szerokość szczelin (100 μm)
screen_distance = 1  # Odległość od ekranu w metrach
screen_width = 0.01  # Szerokość ekranu w metrach
resolution = 500     # Rozdzielczość symulacji

# Położenie szczelin
slit_sources = [(-slit_distance / 2, 0), (slit_distance / 2, 0)]

# Siatka do obliczeń
x = np.linspace(-screen_width / 2, screen_width / 2, resolution)
y = np.linspace(0, screen_distance, resolution)
x_grid, y_grid = np.meshgrid(x, y)

# Tworzenie wykresu
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 9))
plt.subplots_adjust(bottom=0.35, hspace=0.4)

# Początkowy wykres pola falowego
field = generate_huygens_wave(x_grid, y_grid, slit_sources, wavelength, amplitude, screen_distance, slit_width)
im = ax1.imshow(field, extent=[-screen_width / 2, screen_width / 2, 0, screen_distance], aspect='auto', cmap='hot', vmin=0, vmax=0.5)  # Dodane ograniczenie zakresu
ax1.set_xlabel("Pozycja na ekranie (m)", fontsize=10)
ax1.set_ylabel("Odległość od szczelin (m)", fontsize=10)
ax1.set_title("Zasada Hugensa - Pole Falowe", fontsize=12)

# Początkowy wykres intensywności
x_intensity, intensity = calculate_intensity(wavelength, amplitude, slit_distance, screen_distance, screen_width, resolution, slit_width)
line, = ax2.plot(x_intensity, intensity, lw=2, color='blue')
ax2.set_xlabel("Pozycja na ekranie (m)", fontsize=8)
ax2.set_ylabel("Intensywność", fontsize=10)
ax2.set_title("Wzór Interferencyjny", fontsize=12)

# Dodanie suwaków
axcolor = 'lightgoldenrodyellow'
ax_slit_distance = plt.axes([0.15, 0.25, 0.7, 0.03], facecolor=axcolor)
ax_screen_distance = plt.axes([0.15, 0.2, 0.7, 0.03], facecolor=axcolor)
ax_wavelength = plt.axes([0.15, 0.15, 0.7, 0.03], facecolor=axcolor)
ax_amplitude = plt.axes([0.15, 0.1, 0.7, 0.03], facecolor=axcolor)

slider_slit_distance = Slider(ax_slit_distance, 'Odległość szczelin (m)', 1e-4, 5e-3, valinit=slit_distance)
slider_screen_distance = Slider(ax_screen_distance, 'Odległość ekranu (m)', 0.1, 10, valinit=screen_distance)
slider_wavelength = Slider(ax_wavelength, 'Długość fali (m)', 300e-9, 700e-9, valinit=wavelength)
slider_amplitude = Slider(ax_amplitude, 'Amplituda', 0.1, 15, valinit=amplitude)

# Dodanie pól tekstowych na całkowite i średnie natężenie
ax_total_intensity = plt.axes([0.15, 0.05, 0.3, 0.03], facecolor=axcolor)  # Pole dla całkowitego natężenia
ax_avg_intensity = plt.axes([0.55, 0.05, 0.3, 0.03], facecolor=axcolor)  # Pole dla średniego natężenia

text_total_intensity = plt.text(0.5, 0.5, '', transform=ax_total_intensity.transAxes, ha='center', va='center', fontsize=10)
text_avg_intensity = plt.text(0.5, 0.5, '', transform=ax_avg_intensity.transAxes, ha='center', va='center', fontsize=10)

# Funkcja aktualizująca wykresy
def update(val):
    d = slider_slit_distance.val
    L = slider_screen_distance.val
    wl = slider_wavelength.val
    amp = slider_amplitude.val

    # Aktualizacja pola falowego na górnym wykresie
    new_sources = [(-d / 2, 0), (d / 2, 0)]
    new_field = generate_huygens_wave(x_grid, y_grid, new_sources, wl, amp, L, slit_width)
    im.set_data(new_field)  # Aktualizowanie danych wykresu

    # Automatyczne skalowanie do zakresu
    im.set_clim(0, np.max(new_field) * 0.5)

    # Aktualizacja wykresu intensywności
    x_intensity, new_intensity = calculate_intensity(wl, amp, d, L, screen_width, resolution, slit_width)
    line.set_ydata(new_intensity)  # Aktualizacja danych intensywności
    line.set_xdata(x_intensity)   # Aktualizacja danych pozycji

    # Dynamically adjust the y-axis limits of the intensity plot based on the maximum intensity
    ax2.set_ylim(0, np.max(new_intensity) * 1.1)

    # Aktualizacja pól tekstowych
    total_intensity = np.sum(new_intensity)  # Całkowite natężenie
    avg_intensity = np.mean(new_intensity)  # Średnie natężenie

    text_total_intensity.set_text(f'Całkowite natężenie: {total_intensity:.2f}')
    text_avg_intensity.set_text(f'Średnie natężenie: {avg_intensity:.2f}')

    # Odświeżenie wykresu
    fig.canvas.draw_idle()

# Połączenie suwaków z funkcją aktualizacji
slider_slit_distance.on_changed(update)
slider_screen_distance.on_changed(update)
slider_wavelength.on_changed(update)
slider_amplitude.on_changed(update)

plt.show()
