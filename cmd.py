#!/usr/bin/env python

from pydub import AudioSegment
import click


@click.command()
@click.option('--path',
              prompt='Path to mp4 file (required)',
              help='Path to input mp4 file')
@click.option('--volume-min',
              default=0,
              prompt='Minimum volume (dBFS)',
              help='Minimum volume in dBFS')
@click.option('--output-path',
              default='output.mp4',
              prompt='Name or path of output file',
              help='Name or path of ouput file')
def cli(path, volume_min, output_path):
    """ CLI interface to create a sample of the loudest segments of an mp4 """

    click.echo('Loading file: %s' % path)
    try:
        song = load_song(path)
    except IOError:
        return click.echo('Invalid file path: %s' % path)

    click.echo('Finding audio samples with volume '
               'greater than or equal to %s dBFS' % volume_min)
    samples, max_dBFS = find_samples(song, volume_min)
    if len(samples) == 0:
        click.echo("No samples found with volume of %s dBFS" % volume_min)
        click.echo("Max volume in this clip is %s dBFS" % max_dBFS)
        click.echo("Exiting...")
        return

    click.echo("Combining %s samples..." % len(samples))
    new_song = stitch(samples)

    click.echo('Saving to file: %s' % output_path)
    new_song.export(output_path, format="mp4")


def load_song(file_path):
    return AudioSegment.from_file(file_path, "mp4")


def find_samples(audio_segment, volume_min=0):
    """ Finds all samples above a minimum volume threshold and max dBFS of slices
    Args:
        audio_segment: pydbug.AudioSegment object
        volume_min: volume threshold minimum for samples returned (in dBFS)
    """
    samples = []
    song_length = len(audio_segment)  # in milliseconds
    max_dBFS = -1 * float('inf')
    start_index = 0
    loud_segment = False

    for i in range(song_length):
        # find max dBFS to help user find a useful dBFS for clip
        current_dBFS = audio_segment[i].dBFS
        max_dBFS = max_dBFS if current_dBFS < max_dBFS else current_dBFS

        # Use dynamic programming to get audio segments
        if not loud_segment and current_dBFS >= volume_min:
            loud_segment = True
            start_index = i
        elif loud_segment:
            if current_dBFS < volume_min:
                loud_segment = False
                samples.append(audio_segment[start_index:i])
            elif i == song_length - 1:
                loud_segment = False
                samples.append(audio_segment[start_index:song_length])

    return samples, max_dBFS


def stitch(samples):
    """ Stich together all music segments """
    return sum(samples, AudioSegment.empty())

if __name__ == '__main__':
    cli()
