import steampy.client
import steampy.utils


def test(api_key, login, password, steam_guard_file):
    with steampy.client.SteamClient(api_key, login, password,
                                    steam_guard_file) as client:
        print(client.get_my_inventory(steampy.utils.GameOptions.TF2))
