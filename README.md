# Pictalyzur: Categorizing Instagram photos for targeted advertising

The goal of this project is to use image classification to determine what activities a user is interested in, and target advertising accordingly.  

A wearable device is used as an example product.  Twelve image categories were choosen for both their relevance to wearables (e.g. biking, exercise, hiking), and their popularity on Instagram (e.g. pets, food, fashion). 

You can try the web app out for yourself at [http://www.pictalyzur.com/][1].

##Contents
* [Motivation](#motivation)
* [Gathering labeled data](#gld)
* [Model](#model)
* [Web App](#webapp)
* [Installation](#installation)

<a name="motivation"/>
##Motivation

Cognitive psychologists have demonstrated that your memory for an image increases the longer you look at it.  In the world of advertising this means that you want people to view your ads for as long as possible.  One way to achieve this is to to show your product in a domain that is of interest to the consumer.  

Using convolution neural networks, SVD, and logistic regression, I designed a model to categorize social media photos and determine the advertisement that is most likely to engage a specific user.

<a name="gld"/>
##Gathering labeled data

I collected labeled data for thirteen image categories.

###Categories
* Hiking
* Biking
* Hunting and Fishing
* Exercise
* Winter sports
* Beach and Swimming
* Food
* Gardening
* Pets
* Kids
* Night out
* Fashion
* Misc (architecture, signs, etc.)

A large number of images (36,472) were used to improve the generalizability of the model.  The images were collected from the Google Image API and ImageNet.  The images were scaled to dimensions of 256X256 during the download processes for compatibility with the convolution neural network, and irrelevant images were removed prior to training

<a name="model"/>
##Model

![pipeline](https://github.com/wbush008/Pictalyzur/blob/master/imgs/pipeline.png)

One of the major challenges with image data is creating meaningful features from the raw pixels.  For feature construction, I used a convolution neural network that had been pre-trained on image data for an object recognition task.  The network is available through the open source [Caffe][2] toolkit.  

For each image, I extracted 4096 feature values at the first hidden layer of the network.  These 4096 features were then reduced down to 200 using singular value decomposition (SVD).  This reduction made fitting the linear classifier more tractable.

The final classification step was performed using a multinomial logistic regression using a one-vs-rest scheme.  The performance of the model was tested using cross-validation, and the final model achieved 80.8% accuracy.  

The logistic regression was compared with other classifiers, including SVMs, random forest, and gradient boosting.  All of the classifiers showed similar performance, within 3% accuracy, but none outperformed the logistic regression.  It is likely that with an extensive hyper-parameter search these models could surpass the regression, however more efficient improvement could probably be made by creating more extensive training image sets.  

The code for fitting and saving the model is [here][3] in the model_code folder.

<a name="rwd"/>
##Real world data

The trained model is used to label photos from Instagram.  Instagram is an appealing case study for image classification as photos are the primary, and nearly the only, source of information about its users.

![images](https://github.com/wbush008/Pictalyzur/blob/master/imgs/imcats.png)

The application takes an Instagram user name, collects all of the photos in that users feed, and returns a label for each image along with a confidence rating for that label.  This bag of labeled photos can then be used to extract descriptive statistics about the user.  I recorded counts of photos in each category, and importantly the category with the most photos represented in the users feed.  

![plot+ad](https://github.com/wbush008/Pictalyzur/blob/master/imgs/jt_ad.png)

The topic with the largest percentage of photos in the feed is selected as the category of interest for that user.  Using this, I can choose a product ad for that users.  For instance if most of the users photos are of goig out to bars and concerts, they will be served an ad for a smart watch in a night lifescene, where the user will likely to want to engage with the product.  

The code for labeling user photos is [here][4] in the model_code folder.

<a name="webapp"/>
##Web App

The Instagram categorization stage of the model has been integrated into a website at [pictalyzur.com][1].  On the front page of the website you can enter an Instagram username.  This will only work for public Instagram accounts.  It can take a minute or two to collect and classify all of the users images, so you might wanna go grab a coffee while you wait.

Once the images are classified, the website will display statistics for the user.  The two primary pieces of information are the percentage of photos in each category, and the best fit advertisement.  In addition, a dozen of the users images are displayed with their associated labels.  

<a name="installation"/>
##Installation

To run the code in this repo you will need to install Caffe.  Caffe has a great Github [repo][5] as well as a helpful [website][2].  The code in this repo is currently configured to run caffe in GPU mode (which is much faster than CPU mode).  If you want to run it on a computer without a CUDA capable GPU, simply remove the '--gpu' argument from the call to the Caffe network in [PredictUser.py][6] and [BuildFeatures.py][7].  You will also need to make a /bin directory in the repos home directory to store user images, feature arrays, and statistics.


[1]: http://www.pictalyzur.com/ "pictalyzur"
[2]: http://caffe.berkeleyvision.org/ "caffe"
[3]: https://github.com/wbush008/Pictalyzur/blob/master/model_code/BuildModel.py "BuildModel.py"
[4]: https://github.com/wbush008/Pictalyzur/blob/master/model_code/PredictUser.py "PredictUser.py"
[5]: https://github.com/BVLC/caffe "caffe github"
[6]: https://github.com/wbush008/Pictalyzur/blob/master/model_code/PredictUser.py "PredictUser.py"
[7]: https://github.com/wbush008/Pictalyzur/blob/master/model_code/BuildFeatures.py "BuildFeatures.py"
