from mcdreforged.api.all import *
import os
import shutil

CONFIG = \
    {
        'permissions': {
            'start': 2,
            'sync': 2,
            'stop': 2,
            'restart': 2,
            'list': 1
        },
        'this_server': {
            'world_dictionary': 'world/'
        },
        'servers': {
            'default': {
                'name': None,
                'location': '/home/server/server/[11451]mirror',
                'target_region_location': '/home/server/server/[11451]mirror/server/world/region',
                'command': 'screen -dmS mirror bash -c \'python -m mcdreforged\'',
                'rcon': {
                    'enable': True,
                    'port': 19198,
                    'passwd': 'pa55wdHere!'
                }
            }
        }
    }

DATA = {
    'version': '1.0.0'
}


def on_load(server: PluginServerInterface, prev_module):
    config = server.load_config_simple(file_name='config.json', default_config=CONFIG)
    data = server.load_config_simple(file_name='data.json', default_config=DATA)
    permission = config['permissions']
    working_dictionary = server.get_mcdr_config()['working_directory']
    current_server_path = os.getcwd() + f'/{working_dictionary}'
    current_world_dictionary = config['this_server']['world_dictionary']

    server.register_help_message(prefix='!!mirror', message={
        'en_us': 'Mirror Control help',
        'zh_cn': 'Mirror Control 插件帮助'
    })

    @new_thread
    def help_message(source):
        server_list = config['servers']
        source.reply(server.tr('mc.help'))
        for i in server_list.keys():
            text = RTextList(
                RText(server.tr('mc.l.head', server_list[i]['name'])).h(server.tr('mc.l.name', i)),
                RText(server.tr('mc.l.sep')),
                RText(server.tr('mc.l.start')).h(server.tr('mc.l.hint.start')).c(RAction.run_command, f'!!mirror start {i}'),
                RText(server.tr('mc.l.stop')).h(server.tr('mc.l.hint.stop')).c(RAction.run_command, f'!!mirror stop {i}'),
                RText(server.tr('mc.l.restart')).h(server.tr('mc.l.hint.restart')).c(RAction.run_command, f'!!mirror restart {i}'),
                RText(server.tr('mc.l.sync')).h(server.tr('mc.l.hint.sync')).c(RAction.run_command, f'!!mirror sync {i}'),
                RText(server.tr('mc.l.sep'))
            )
            source.reply(text)

    @new_thread
    def start_server(source, ctx):
        server_name = ctx['server_name']
        try:
            if data[server_name]['running'] is True:
                source.reply('mc.server.start.on')
                return
        except KeyError:
            pass
        try:
            server_location = config['servers'][server_name]['location']
            server_startup_command = config['servers'][server_name]['command']
            sync_server(source, ctx)
            command = f'cd {server_location} && {server_startup_command}'
            source.reply(server.tr('mc.server.start.starting'))
            os.system(command)
            server.logger.info(server.tr('mc.server.start.log.success'))
            try:
                data[server_name]['running'] = True
                server.save_config_simple(config=data, file_name='data.json')
            except KeyError:
                data[server_name] = {}
                data[server_name]['running'] = True
                server.save_config_simple(config=data, file_name='data.json')
        except KeyError:
            source.reply(server.tr("mc.server.key_error"))
            server.logger.info(server.tr('mc.server.start.log.fail'))

    @new_thread
    def sync_server(source, ctx):
        server_name = ctx['server_name']
        try:
            if data[server_name]['running'] is True:
                stop_server(source, ctx)
        except KeyError:
            pass
        try:
            target_region_location = config['servers'][server_name]['target_region_location']
            try:
                shutil.rmtree(target_region_location)
                shutil.copytree(current_server_path + '/' + current_world_dictionary + 'region', target_region_location)
                server.logger.info(server.tr('mc.server.sync.log.d'))
            except FileNotFoundError:
                shutil.copytree(current_server_path + '/' + current_world_dictionary + 'region', target_region_location)
                server.logger.info(server.tr('mc.server.sync.log.r'))
            source.reply(server.tr('mc.server.sync.complete'))
        except KeyError:
            source.reply(server.tr('mc.server.key_error'))
            server.logger.info(server.tr('mc.server.sync.log.fail'))

    @new_thread
    def stop_server(source, ctx):
        server_name = ctx['server_name']
        try:
            if data[server_name]['running'] is False:
                source.reply('mc.server.stop.not_on')
                return
        except KeyError:
            source.reply('mc.server.start.no_data')
            return
        try:
            rcon_port = config['servers'][server_name]['rcon']['port']
            rcon_password = config['servers'][server_name]['rcon']['passwd']
            rcon = RconConnection(address='127.0.0.1', port=rcon_port, password=rcon_password)
            rcon.connect()
            r = rcon.send_command(command='stop')
            print(r)
            if r is not None:
                source.reply(server.tr('mc.server.stop.success'))
                server.logger.info(server.tr('mc.server.stop.log.success'))
                data[server_name]['running'] = False
                return
            source.reply(server.tr('mc.server.stop.fail'))
            server.logger.info(server.tr('mc.server.stop.log.fail'))

        except KeyError:
            source.reply(server.tr('mc.server.key_error'))
            server.logger.info(server.tr('mc.server.stop.log.fail'))

    @new_thread
    def restart_server(source, ctx):
        server_name = ctx['server_name']
        try:
            if data[server_name]['running'] is False:
                source.reply('mc.server.stop.not_on')
                return
        except KeyError:
            source.reply('mc.server.start.no_data')
            return
        stop_server(source, ctx)
        start_server(source, ctx)

    server.register_command(
        Literal('!!mirror'). \
        then(
            Literal('start').
            then(
                Text('server_name').
                requires(lambda src: src.has_permission(permission['start'])).
                runs(start_server)
            ).
            runs(lambda src: src.reply(server.tr('mc.server.command.blank_server_name')))
        ). \
        then(
            Literal('sync').
            then(
                Text('server_name').
                requires(lambda src: src.has_permission(permission['sync'])).
                runs(sync_server)
            ).
            runs(lambda src: src.reply(server.tr('mc.server.command.blank_server_name')))
        ). \
        then(
            Literal('stop').
            then(
                Text('server_name').
                requires(lambda src: src.has_permission(permission['stop'])).
                runs(stop_server)
            ).
            runs(lambda src: src.reply(server.tr('mc.server.command.blank_server_name')))
        ). \
        then(
            Literal('restart').
            then(
                Text('server_name').
                requires(lambda src: src.has_permission(permission['restart'])).
                runs(restart_server)
            ).
            runs(lambda src: src.reply(server.tr('mc.server.command.blank_server_name')))
        ). \
        runs(help_message)
    )
