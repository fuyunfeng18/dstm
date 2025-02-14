import argparse
from input_fn import *
from model.lda import *


def parse_args():
    parser = argparse.ArgumentParser(description='Description the Command Line of LDA Model')
    parser.add_argument('--data_source', help='Select data source: neuroscience(neuro), bioinformatics(bio), '
                                              '(default = %(default)s)', default='bio', choices=['bio', 'neuro'])
    parser.add_argument('--mode', help='Choose mode: estimate (est), inference (inf), or demonstration (demo) '
                                       '(default = %(default)s)', default='demo', choices=['est', 'inf', 'demo'])
    parser.add_argument('--run_mode', help='Run model from start or continue, (default = %(default)s)',
                        default='start', choices=['start', 'continue'])
    parser.add_argument('--num_iterations', help='Number of iterations (default = %(default)s)', type=int,
                        default=1, choices=range(0, 2000), metavar='(0, ..., 2000)')
    parser.add_argument('--num_topics', help='Number of topics (default = %(default)s)', type=int,
                        default=1000, choices=range(1, 5001), metavar='(1, ..., 5000)')
    parser.add_argument('--seed', help='Set the seeds (default = %(default)s)', type=float,
                        default=7, choices=range(1, 1001), metavar='(1, ..., 1000)')
    parser.add_argument('--verbose', help='show performance debug information (default = %(default)s)', type=int,
                        default=1, choices=[0, 1])
    parser.add_argument('--model_folder', help='Specify the model folder name for running continuously. '
                                               'If running from start it will create a model by default', type=str)
    parser.add_argument('--evaluate', help='choose whether model evaluation or not '
                                           '(default = %(default)s)', default='no', choices=['no', 'yes'])
    parser.add_argument('--save', help='choose whether save model or not '
                                        '(default = %(default)s)', default='no', choices=['no', 'yes'])

    args = parser.parse_args()

    # provide basic checking
    if args.run_mode == 'continue' and args.model_folder is None:
        parser.error('model_folder is required when run_mode is continue')

    if args.mode == 'inf' and args.model_folder is None:
        parser.error('model_folder is required when mode is inf')

    return args


def main():
    print "Program start."
    # get parameters from arguments
    args = parse_args()

    # get inputs data
    inputs = input_fn(args.mode, args.data_source)

    if (args.mode == "est" or args.mode == 'demo') and args.run_mode == 'start':

        # set the hyper-parameters
        inputs['mode'] = args.mode
        inputs['run_mode'] = args.run_mode
        inputs['num_topics'] = args.num_topics
        inputs['num_iterations'] = args.num_iterations
        inputs['verbose'] = args.verbose
        inputs['model_folder'] = args.model_folder
        inputs['seed'] = args.seed
        inputs['alpha'] = 50.0 / args.num_topics
        inputs['beta'] = 0.1
        inputs['data_source'] = args.data_source
        inputs['num_vocabs'] = len(inputs['vocab'])  # number of vocabularies
        inputs['num_docs'] = len(inputs['docs'])  # number of documents

        print "The model mode is: " + str(inputs['mode'])
        print "The data source is: " + str(inputs['data_source'])
        print "The number of vocabularies: " + str(inputs['num_vocabs'])
        print "The number of documents: " + str(len(inputs['docs']))
        print "The number of topics: " + str(inputs['num_topics'])
        print "The number of iterations: " + str(inputs['num_iterations'])
        print "The alpha is " + str(inputs['alpha'])
        print "The beta is " + str(inputs['beta'])
        sys.stdout.flush()

        # (1) Model initialization
        model = LDA(inputs)
        model.model_init(inputs)

        # (2) Run gibbs sampling algorithm
        model.gibbs()

        # (3) Save model file
        if args.save == "yes":
            model.save()

        # (4) Model evaluation
        if args.evaluate == "yes":
            model.harmonic_mean()

    # Model running as continue
    if args.run_mode == 'continue' and args.mode != 'inf':
        inputs['mode'] = args.mode
        inputs['run_mode'] = 'continue'
        inputs['num_iterations'] = args.num_iterations
        inputs['model_folder'] = args.model_folder
        inputs['num_vocabs'] = len(inputs['vocab'])  # number of vocabularies
        inputs['num_docs'] = len(inputs['docs'])  # number of documents
        inputs['num_tools'] = len(inputs['tools'])  # number of tools
        inputs['num_datasets'] = len(inputs['datasets'])  # number of datasets

        # (1) Model initialization (load model file)
        model = LDA(inputs)
        model.model_init(inputs)

        # (2) Run gibbs sampling algorithm
        model.gibbs()

        # (3) Save model file
        model.save()

    # Model inference
    if args.mode == "inf":
        inputs['mode'] = args.mode
        inputs['run_mode'] = 'continue'
        inputs['model_folder'] = args.model_folder
        inputs['num_vocabs'] = len(inputs['vocab'])  # number of vocabularies
        inputs['num_docs'] = len(inputs['docs'])  # number of documents
        inputs['num_tools'] = len(inputs['tools'])  # number of tools
        inputs['num_datasets'] = len(inputs['datasets'])  # number of datasets
        inputs['num_iterations'] = 0                   # no need iterations

        # (1) Model initialization (load model file)
        model = LDA(inputs)
        model.model_init(inputs)

        # run model inference
        model.inference()

    print "Program end."


if __name__ == "__main__":
    main()
