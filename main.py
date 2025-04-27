import dearpygui.dearpygui as dpg
import threading
import platform
import win32api
import win32con
import random
import time

def get_hz():
    device_index = 0
    display_id = 1
    displays = []

    while True:
        try:
            device = win32api.EnumDisplayDevices(None, device_index)
            if not device.DeviceName:
                break

            settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
            display_info = {
                'id': display_id,
                'name': device.DeviceString,
                'refresh_rate': settings.DisplayFrequency
            }
            displays.append(display_info)

            device_index += 1
            display_id += 1
        except:
            break

    return displays


def get_fps():
    return dpg.get_frame_rate()


def start_thread(target, *args):
    try:
        thread = threading.Thread(target=target, args=args)
        thread.daemon = True
        thread.start()
        return thread
    except Exception as e:
        raise e
    
def start_game():
    global game_running
    if not game_running:
        game_running = True
        threading.Thread(target=game_loop, daemon=True).start()

def game_loop():
    global current_action, action_time, selected_text_tag, game_running, awaiting_reaction

    if not game_running:
        return

    dpg.set_value("text1", "")
    dpg.set_value("text2", "")

    selected_text_tag = random.choice(["text1", "text2"])

    wait_time = random.uniform(1, 5)
    start_wait = time.perf_counter()
    while time.perf_counter() - start_wait < wait_time:
        time.sleep(0.001)
        if not game_running:
            return

    if not game_running:
        return

    current_action = random.choice(["Attack!", "Feint!"])

    if current_action:
        dpg.set_value(selected_text_tag, current_action)
        action_time = time.perf_counter()
        awaiting_reaction = True  # <<< waiting for player now

        if current_action == "Feint!":
            feint_start = time.perf_counter()
            while time.perf_counter() - feint_start < 0.5:
                time.sleep(0.001)
                if not game_running:
                    return
            if game_running and awaiting_reaction:
                dpg.set_value("text1", "")
                dpg.set_value("text2", "")
                current_action = None
                action_time = 0
                awaiting_reaction = False
                threading.Thread(target=game_loop, daemon=True).start()
    else:
        dpg.set_value(selected_text_tag, "")
        action_time = 0


def parry_pressed():
    global game_running, current_action, action_time, awaiting_reaction

    if not game_running or not awaiting_reaction:
        return

    if action_time == 0 and current_action is None:
        return

    now = time.perf_counter()
    fps = int(get_fps())

    if current_action == "Attack!":
        reaction_time = (now - action_time) * 1000

        if reaction_time < 120:
            judgement = "Godlike"
        elif reaction_time < 140:
            judgement = "Elite"
        elif reaction_time < 160:
            judgement = "Pro"
        elif reaction_time < 180:
            judgement = "Semi-Pro"
        elif reaction_time < 200:
            judgement = "Advanced"
        elif reaction_time < 220:
            judgement = "Good"
        elif reaction_time < 240:
            judgement = "Average"
        elif reaction_time < 260:
            judgement = "Below Average"
        elif reaction_time < 280:
            judgement = "Slow"
        else:
            judgement = "Noob"

        items.append(f"{judgement} - {fps}fps {int(reaction_time)}ms")

    elif current_action == "Feint!" and action_time != 0:
        items.append("Mistake")

    dpg.set_value("text1", "")
    dpg.set_value("text2", "")

    dpg.configure_item('listbox', items=items)

    current_action = None
    action_time = 0
    awaiting_reaction = False

    if game_running:
        threading.Thread(target=game_loop, daemon=True).start()


def stop_game():
    global game_running
    game_running = False


def main():    
    dpg.create_context()

    with dpg.window(tag="Primary Window"):
        with dpg.group(horizontal=True):
            dpg.add_button(label='Start', width=100, callback=start_game)
            dpg.add_button(label='Parry', width=368, callback=parry_pressed)
            
        with dpg.group(horizontal=True):
            dpg.add_listbox(items=items, tag='listbox')
            with dpg.child_window(height=75):
                dpg.add_text(tag='text1')
                dpg.add_text(tag='text2')

        displays = get_hz()
        for display in displays:
            dpg.add_text(f"Display {display['id']}: {display['name']} - {display['refresh_rate']} Hz")

    with dpg.handler_registry():
        dpg.add_key_release_handler(key=dpg.mvKey_Spacebar, callback=start_game)

    with dpg.window(tag="Popup window", show=False, modal=True, autosize=True):
        dpg.add_text(tag="Popup text")

    with dpg.font_registry():
        default_font = dpg.add_font("FiraCode-Medium.ttf", 17)
    dpg.bind_font(default_font)

    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 2)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 2)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 2)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 2)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 2)

            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (70, 70, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (100, 100, 100, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, (30, 30, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20, 20, 20, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, (50, 50, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60, 60, 60, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 30, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_DockingPreview, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (70, 70, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (80, 80, 80, 255))
            dpg.add_theme_color(dpg.mvThemeCol_DockingEmptyBg, (10, 10, 10, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Header, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_PlotLines, (100, 100, 100, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 70, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_PlotLinesHovered, (110, 110, 110, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (60, 60, 60, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (50, 50, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (100, 100, 100, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Separator, (60, 60, 60, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (50, 50, 50, 255))
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotHistogramHovered, (110, 110, 110, 255)
            )
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, (80, 80, 80, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (60, 60, 60, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, (50, 50, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (30, 30, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, (60, 60, 60, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGrip, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (50, 50, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, (80, 80, 80, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGripHovered, (60, 60, 60, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (20, 20, 20, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, (30, 30, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGripActive, (70, 70, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (10, 10, 10, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Tab, (20, 20, 20, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (10, 10, 10, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, (70, 70, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (50, 50, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_DragDropTarget, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (60, 60, 60, 255))
            dpg.add_theme_color(dpg.mvThemeCol_NavHighlight, (80, 80, 80, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (80, 80, 80, 255))
            dpg.add_theme_color(
                dpg.mvThemeCol_NavWindowingHighlight, (100, 100, 100, 255)
            )
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (150, 150, 150, 255))
            dpg.add_theme_color(dpg.mvThemeCol_NavWindowingDimBg, (30, 30, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (70, 70, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (10, 10, 10, 255))

    dpg.bind_theme(theme)

    dpg.create_viewport(
        title=f"{title} by {author}",
        width=750,
        height=765,
        clear_color=(15, 15, 15, 255),
        resizable=False,
    )
    dpg.show_metrics()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    title = "Instant Awareness & Reflex Trainer"
    author = "@batubyte"
    update_date = "4/27/2025"

    items = []
    game_running = False
    current_action = None
    action_time = 0
    selected_text_tag = None

    if platform.system() == "Windows":
        main()
    else:
        print("Linux soon.")
